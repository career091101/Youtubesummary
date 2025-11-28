import csv
import os
import sys
from googleapiclient.discovery import build
from src.config import Config

def get_channel_id_from_handle(youtube, handle):
    try:
        response = youtube.channels().list(
            part='id',
            forHandle=handle
        ).execute()
        if response['items']:
            return response['items'][0]['id']
    except Exception as e:
        print(f"Error resolving handle {handle}: {e}")
    return None

def get_channel_id_from_username(youtube, username):
    try:
        response = youtube.channels().list(
            part='id',
            forUsername=username
        ).execute()
        if response['items']:
            return response['items'][0]['id']
    except Exception as e:
        print(f"Error resolving username {username}: {e}")
    return None

def update_channel_ids():
    if not Config.validate():
        print("Invalid configuration. Check .env file.")
        return

    youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)

    csv_path = 'generative_ai_channels.csv'
    txt_path = 'channel_ids.txt'

    existing_ids = set()
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            existing_ids = set(line.strip() for line in f if line.strip())

    print(f"Loaded {len(existing_ids)} existing channel IDs.")

    new_ids = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row['Channel URL']
            channel_id = None

            if '/channel/' in url:
                channel_id = url.split('/channel/')[-1]
            elif '/@' in url:
                handle = '@' + url.split('/@')[-1]
                print(f"Resolving handle: {handle}")
                channel_id = get_channel_id_from_handle(youtube, handle)
            elif '/user/' in url:
                username = url.split('/user/')[-1]
                print(f"Resolving username: {username}")
                channel_id = get_channel_id_from_username(youtube, username)
            elif '/c/' in url:
                # Custom URL, harder to resolve directly without search or scraping
                # Try search
                query = url.split('/c/')[-1]
                print(f"Searching for custom URL: {query}")
                try:
                    response = youtube.search().list(
                        part='snippet',
                        q=query,
                        type='channel',
                        maxResults=1
                    ).execute()
                    if response['items']:
                        channel_id = response['items'][0]['snippet']['channelId']
                except Exception as e:
                    print(f"Error searching for {query}: {e}")
            else:
                # Try direct search with channel name if URL format is unknown or just a custom name
                # But be careful not to add wrong channels.
                # For now, skip unknown formats or try to parse if it looks like a custom URL
                pass

            if channel_id:
                if channel_id not in existing_ids:
                    print(f"Found new ID: {channel_id} for {url}")
                    new_ids.append(channel_id)
                    existing_ids.add(channel_id)
                else:
                    # print(f"ID already exists: {channel_id}")
                    pass
            else:
                print(f"Could not resolve ID for: {url}")

    if new_ids:
        with open(txt_path, 'a', encoding='utf-8') as f:
            for cid in new_ids:
                f.write(f"{cid}\n")
        print(f"Added {len(new_ids)} new channel IDs to {txt_path}.")
    else:
        print("No new channel IDs found.")

if __name__ == "__main__":
    update_channel_ids()
