import scrapetube
from db import YouTubeDatabase


def get_videos(channel_name, db, num_videos=5):
    '''
    :param channel_id: id of desired channel
    :param db: of last youtube videos done
    :param num_videos: number of videos to retrieve
    :return: list of urls found after the last video
    '''
    # Get the video generator for the channel
    channel_id = db.get_random_fetch_channel_id(channel_name)

    videos = scrapetube.get_channel(channel_id)

    # Retrieve the last URL for the given channel from the database
    last_url = db.get_last_link(channel_name, channel_id)

    # Initialize an empty list to store the URLs
    urls = []

    # Flag to start appending URLs
    append_urls = False

    if last_url is None or len(last_url) == 0:
        append_urls = True

    # Iterate over the video generator
    for video in videos:
        url = f'https://www.youtube.com/watch?v={video["videoId"]}'


        # If we've reached the last URL from the database, set the flag to start appending URLs
        if url == last_url:
            append_urls = True
            continue

        # If the flag is set, append the URL to the list
        if append_urls:
            urls.append(url)

        # If we have num_videos URLs, break the loop
        if len(urls) == num_videos:
            break

    return urls

if __name__ == "__main__":
    db = YouTubeDatabase(r'../youtube_links.db')
    videos = get_videos("Briefly Hilarious", db)
    print(videos)
