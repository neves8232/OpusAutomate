import sys
import threading
import requests
import httpx
import json
from time import sleep
from seleniumbase import Driver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
import urllib.parse
from pathlib import Path
from utils import settings
from utils.logger import ColorLogger
from utils.db import UserDatabase, YouTubeDatabase
import time
import re
from utils.utils import get_yt_video_length as yt_length

logger = ColorLogger()

add_printer(1)

directory = Path().absolute()

config = settings.check_toml(
    f"{directory}/utils/.config.template.toml", f"{directory}/config.toml"
)
config is False and sys.exit()


def get_df_simple(driver, selector="*", error="", step="", max_retries=50, timeout=None):
    df = pd.DataFrame()

    start_time = time.time()
    retries = 0

    while df.empty:
        df = get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector=selector,
            with_methods=True,
        )

        if df.empty:
            if error:
                logger.error(error)
            sleep(1)
            retries += 1

        # Check for max retries
        if max_retries and retries >= max_retries:
            return pd.DataFrame()

        # Check for timeout
        if timeout and (time.time() - start_time) > timeout:
            return pd.DataFrame()

    logger.step(step)
    return df


class Opus():

    def __init__(self, yt_link=None, username=None, domain=None, proxy_country="pt", clip_url=None):
        self.headless = config["driver"]["headless"]
        self.proxy = self.get_proxy(proxy_country)
        self.driver = Driver(uc=True, proxy=self.proxy, headless=self.headless)
        self.username = username
        self.domain = domain
        self.channel = config["video_settings"]["channel"]
        self.yt_link = yt_link
        self.clip_url = clip_url

        channel = config["video_settings"]["channel"]
        path_video = config["video_settings"]["path_video"]
        self.path = path_video + "\\" + channel + "\\"
        self.num_short = config["video_settings"]["num_shorts"]

    def run(self):
        if self.username and self.clip_url:
            self.login(self.clip_url)
            sleep(10)
            while not self.check_available():
                sleep(30)

            self.download()
            db.update_user_link(self.username, "")
            self.driver.quit()

        else:
            account = self.see_if_account_available()
            if account:
                self.username, self.domain = account[1], account[2]
                logger.step(f"Using account {self.username} with {account[3]} duration")

                self.login()
            else:
                self.login()
                self.trial()

            clips_link = self.iniciar_cortes()
            sleep(10)
            time_left = self.time_left()
            yt_db.add_video(self.yt_link)
            if time_left > 20:
                db.insert_or_update_data(self.username, self.domain, time_left, clips_link)

            else:
                db.delete_user_from_db(self.username)
            sleep(10)
            while not self.check_available():
                sleep(30)

            self.download()
            db.update_user_link(self.username, "")
            self.driver.quit()

    def see_if_account_available(self):
        yt_duration = yt_length(self.yt_link)
        for account in db.get_data():
            time_left = account[3]

            if time_left > yt_duration or time_left == 90 \
                    or (time_left >= 60 and yt_duration > 90):
                db.delete_user_from_db(account[1])
                return account

        return None

    def get_proxy(self, country):
        proxy = f"nkwepjpyvw5xrgy-country-{country}:bcbdmvopoo5ek1k@rp.proxyscrape.com:6060"
        return proxy

    def login(self, url="https://clip.opus.pro/dashboard"):
        new = False

        if not self.username:
            self.username, self.domain = Email.get_email()
            new = True

        email = self.username + "@" + self.domain

        self.driver.get(url)

        email_df = get_df_simple(self.driver, 'input[placeholder="Enter email address"]',
                                 error="Couldn't find email placeholder",
                                 step="Found email placeholder")

        email_df.iloc[0].se_send_keys(email)

        continue_btn = get_df_simple(self.driver, 'button[type="submit"]', error="Couldn't find continue button",
                                     step="Clicking the continue button")
        continue_btn.iloc[0].se_click()

        if not new:
            logger.step("Waiting for email")
            sleep(60)

        codigo = Email.get_code(self.username, self.domain)

        verification = get_df_simple(self.driver, 'input[placeholder="Enter verification code"]',
                                     error="Couldn't find verification placeholder",
                                     step="Found verification placeholder")
        verification.iloc[0].se_send_keys(codigo)

        continue_btn = get_df_simple(self.driver, 'button[type="submit"]', error="Couldn't find continue button",
                                     step="Clicking the continue button")
        continue_btn.iloc[0].se_click()

        return self.username, self.domain

    def trial(self):
        start_trial = get_df_simple(self.driver, 'button[type="button"]')
        while True:
            try:
                start = \
                    start_trial.loc[
                        start_trial.aa_textContent.str.contains("Start clipping", regex=False, na=False)].iloc[0]
                start.se_click()
                logger.step("Clicked Start Trial")
                break
            except:
                start_trial = get_df_simple(self.driver, 'button[type="button"]')
                logger.error("Couldn't find Start Trial")

        popup = get_df_simple(self.driver,
                              '#intercom-container > div > div > div > div > div.intercom-tour-step-header > span',
                              error="Couldn't find popup",
                              step="Closing popup",
                              timeout=60)

        if not popup.empty:
            popup.iloc[0].se_click()

    def iniciar_cortes(self):
        yt_placeholder = get_df_simple(self.driver, 'input[placeholder="Drop a video link"]',
                                       error="Couldn't find video link placeholder",
                                       step="Found video link placeholder")

        yt_placeholder.iloc[0].se_send_keys(self.yt_link)

        get_clips = get_df_simple(self.driver, 'button[type="button"]')

        while True:

            url_atual = self.driver.current_url

            if "dashboard" in url_atual:
                try:
                    get_clips.loc[
                        get_clips.aa_textContent.str.contains('Get clips in 1 click', regex=False, na=False)].iloc[
                        0].se_click()

                except:
                    get_clips = get_df_simple(self.driver, 'button[type="button"]',
                                              error="Couldn't click Get clips",
                                              step="Clicking Get clips"
                                              )

            else:
                return url_atual

    def time_left(self):
        current_time = get_df_simple(self.driver, "p")
        current_time = current_time.loc[
            current_time.aa_parentElement.str.contains('HTMLDivElement', regex=False, na=False)].iloc[
            0].aa_outerText

        hours_match = re.search(r'(\d+)h', current_time)
        minutes_match = re.search(r'(\d+)m', current_time)

        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0

        return hours * 60 + minutes

    def check_available(self):
        df = get_df(
            self.driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector="*",
            with_methods=True,
        )

        make_video = df.loc[df.aa_outerText.str.contains("Fetching video", regex=False, na=False)]

        if not make_video.empty:
            logger.error("Waiting for Opus to create clips")
            return False
        else:
            logger.step("Clips available")
            return True

    def download(self):
        def buscar_videos():
            df = get_df(
                self.driver,
                By,
                WebDriverWait,
                expected_conditions,
                queryselector="*",
                with_methods=True,
            )
            link_download = df.loc[df.aa_href.str.contains('mp4', regex=False, na=False)].head(
                self.num_short)  # links de download

            return [row['aa_href'] for index, row in link_download.iterrows()]

        def download_do_video(links):
            for link in links:
                parsed_url = urllib.parse.urlparse(link)
                file_name = urllib.parse.unquote(parsed_url.path.split('/')[-1])

                # Send an HTTP GET request to the URL
                response = requests.get(link)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Specify the local file path where you want to save the video
                    local_file_path = self.path + file_name  # Use the extracted file name

                    # Open the local file in binary write mode and write the content from the response
                    with open(local_file_path, 'wb') as f:
                        f.write(response.content)

                    logger.step(f"Video downloaded and saved as {local_file_path}")
                else:
                    logger.error(f"Failed to download the video. Status code: {response.status_code}")

        links = buscar_videos()
        download_do_video(links)


class Email:
    @staticmethod
    def get_email():
        url = "https://www.1secmail.com/api/v1/?action=genRandomMailbox"
        result = requests.get(url)

        data = json.loads(result.text)
        email = data[0]
        username, domain = email.split('@')
        return username, domain

    @staticmethod
    def get_code(username, domain, subject_codigo="OpusClip"):
        for _ in range(30):
            url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
            data = httpx.get(url).json()
            for email in data:
                if subject_codigo in email["subject"]:
                    codigo = email["subject"].split()[0]
                    logger.step(f"Código: {codigo}")
                    return codigo

            logger.error("Ainda nao ha codigo")
            sleep(5)

        logger.error("Não recebemos código")
        return False


def videos_to_be_done():
    videos_already_done = yt_db.get_all_links()
    videos_to_be_done = []
    for link in config["video_settings"]["yt_links"]:
        if link not in videos_already_done:
            videos_to_be_done.append(link)

    return videos_to_be_done


def main():
    #
    #       TO BE FIXED LOGIC OF DOWNLOADING ALREADY COMPILED CLIPS
    #
    # for account in db.get_data():
    #     if account[4]: #if there's any clips left to be downloaded
    #         conta = Opus(clip_url=account[4], username=account[1], domain=account[2])
    #         conta.run()

    videos = videos_to_be_done()

    # Create and start a thread for each video link
    for link in videos:
        conta = Opus(yt_link=link)
        conta.run()


db = UserDatabase()
yt_db = YouTubeDatabase()

if __name__ == "__main__":
    main()
