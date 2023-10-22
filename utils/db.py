import sqlite3
import os
import random

class UserDatabase:
    def __init__(self, db_name='user_data.db'):
        self.db_name = db_name
        if not os.path.exists(self.db_name):
            self.initialize_db()

    def initialize_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    time_left INTEGER NOT NULL,
                    clips TEXT NOT NULL
                )
            ''')

    def update_user_link(self, user, new_link):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE user_info SET clips=? WHERE user=?', (new_link, user))

    def insert_or_update_data(self, user, domain, time_left, clips):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Check if user already exists
            cursor.execute('SELECT * FROM user_info WHERE user=?', (user,))
            data = cursor.fetchone()

            if data:
                # If user exists, update the data
                self.update_user_data(user, domain, time_left, clips)
            else:
                # If user does not exist, insert new data
                cursor.execute('''
                    INSERT INTO user_info (user, domain, time_left, clips)
                    VALUES (?, ?, ?, ?)
                ''', (user, domain, time_left, clips))

    def get_data(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_info')
            data = cursor.fetchall()
        return data

    def update_user_data(self, user, domain=None, time_left=None, clips=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if domain:
                cursor.execute('UPDATE user_info SET domain=? WHERE user=?', (domain, user))
            if time_left is not None:
                cursor.execute('UPDATE user_info SET time_left=? WHERE user=?', (time_left, user))
            if clips is not None:
                cursor.execute('UPDATE user_info SET clips=? WHERE user=?', (clips, user))

    def delete_user_from_db(self, user):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_info WHERE user=?', (user,))

class YouTubeDatabase:
    def __init__(self, db_name='youtube_links.db'):
        self.db_name = db_name
        if not os.path.exists(self.db_name):
            self.initialize_db()

    def initialize_db(self):
        """Initialize the database and create the table if it doesn't exist."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS youtube_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_name TEXT NOT NULL,
                    fetch_channel_id TEXT NOT NULL,
                    link TEXT NOT NULL,
                    UNIQUE (channel_name, fetch_channel_id, link)
                )
            ''')

    def add_video(self, channel_name, fetch_channel_id, link):
        """Add a YouTube link to the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO youtube_links (channel_name, fetch_channel_id, link)
                    VALUES (?, ?, ?)
                ''', (channel_name, fetch_channel_id, link))
            except sqlite3.IntegrityError:
                # This will occur if the link is already in the database due to the UNIQUE constraint.
                print(f"Link {link} is already in the database for channel {channel_name} with fetch channel ID {fetch_channel_id}.")

    def delete_video(self, channel_name, fetch_channel_id, link):
        """Delete a YouTube link from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM youtube_links
                WHERE channel_name=? AND fetch_channel_id=? AND link=?
            ''', (channel_name, fetch_channel_id, link))

    def get_random_fetch_channel_id(self, channel_name):
        """Retrieve a random fetch_channel_id for a given channel_name."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fetch_channel_id FROM youtube_links
                WHERE channel_name=?
            ''', (channel_name,))
            fetch_channel_ids = [row[0] for row in cursor.fetchall()]
            if fetch_channel_ids:
                return random.choice(fetch_channel_ids)
            return None

    def get_last_link(self, channel_name, fetch_channel_id):
        """Retrieve the last YouTube link added for a given channel_name and fetch_channel_id."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT link FROM youtube_links
                WHERE channel_name=? AND fetch_channel_id=?
                ORDER BY id DESC LIMIT 1
            ''', (channel_name, fetch_channel_id))
            link = cursor.fetchone()
            if link:
                return link[0]
            return None

    def display_db(self):
        """Display all entries in the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM youtube_links')
            rows = cursor.fetchall()
            print(f"{'ID':<5} {'Channel Name':<20} {'Fetch Channel ID':<20} {'Link'}")
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<20} {row[3]}")

    def get_all_links(self):
        """Retrieve all YouTube links from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT link FROM youtube_links')
            links = [row[0] for row in cursor.fetchall()]
        return links

# if __name__ == '__main__':
db = UserDatabase(r'../user_data.db')
db.get_data()