import json
import csv
import re
from datetime import datetime

# File paths
WATCH_HISTORY_FILE = '/Users/y-sato/Downloads/Youtube要約/watch-history.json'
SUBSCRIPTIONS_FILE = '/Users/y-sato/Downloads/Youtube要約/登録チャンネル.csv'
OUTPUT_VIDEOS_FILE = 'extracted_ai_tech_videos.csv'
OUTPUT_CHANNELS_FILE = 'extracted_ai_tech_channels.csv'

# Keywords for filtering
KEYWORDS = [
    # Japanese
    "生成AI", "人工知能", "機械学習", "深層学習", "プログラミング", "エンジニア", 
    "テック", "ガジェット", "開発", "コード", "アプリ", "ソフトウェア", "データサイエンス",
    "アルゴリズム", "クラウド", "セキュリティ", "ロボット", "IT", "DX", "SaaS",
    
    # English
    "Generative AI", "AI", "ChatGPT", "LLM", "Gemini", "Claude", "Copilot", 
    "OpenAI", "Anthropic", "Google", "NVIDIA", "Python", "JavaScript", "TypeScript", 
    "Coding", "Programming", "Tech", "Technology", "Gadget", "Review", "Engineer", 
    "Developer", "Software", "Data Science", "Algorithm", "Cloud", "Security", "Robot"
]

def is_relevant(text):
    if not text:
        return False
    text_lower = text.lower()
    
    # Japanese keywords (simple substring match)
    jp_keywords = [
        "生成AI", "人工知能", "機械学習", "深層学習", "プログラミング", "エンジニア", 
        "テック", "ガジェット", "開発", "コード", "アプリ", "ソフトウェア", "データサイエンス",
        "アルゴリズム", "クラウド", "セキュリティ", "ロボット", "DX", "SaaS"
    ]
    for k in jp_keywords:
        if k.lower() in text_lower:
            return True
            
    # English/Short keywords (use regex for word boundaries)
    # "IT" is removed from general substring match and added here with boundaries
    # "AI" is also better with boundaries to avoid "mail", "rain" etc.
    en_keywords = [
        "Generative AI", "AI", "ChatGPT", "LLM", "Gemini", "Claude", "Copilot", 
        "OpenAI", "Anthropic", "Google", "NVIDIA", "Python", "JavaScript", "TypeScript", 
        "Coding", "Programming", "Tech", "Technology", "Gadget", "Review", "Engineer", 
        "Developer", "Software", "Data Science", "Algorithm", "Cloud", "Security", "Robot",
        "IT"
    ]
    
    for k in en_keywords:
        # Escape keyword just in case, though these are safe
        pattern = r'(?<![a-zA-Z])' + re.escape(k.lower()) + r'(?![a-zA-Z])'
        if re.search(pattern, text_lower):
            return True
            
    return False

def extract_channel_id(url):
    if not url:
        return ""
    # Typical format: https://www.youtube.com/channel/UC...
    match = re.search(r'channel/(UC[\w-]+)', url)
    if match:
        return match.group(1)
    return ""

def process_watch_history():
    print("Processing watch history...")
    relevant_videos = []
    
    try:
        with open(WATCH_HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for entry in data:
            # Extract fields
            title = entry.get('title', '')
            # Remove " を視聴しました" suffix if present (common in Japanese export)
            title = title.replace(" を視聴しました", "")
            
            title_url = entry.get('titleUrl', '')
            time_str = entry.get('time', '')
            
            subtitles = entry.get('subtitles', [])
            channel_name = ""
            channel_url = ""
            if subtitles:
                channel_name = subtitles[0].get('name', '')
                channel_url = subtitles[0].get('url', '')
            
            channel_id = extract_channel_id(channel_url)
            
            # Check relevance
            if is_relevant(title) or is_relevant(channel_name):
                relevant_videos.append({
                    'title': title,
                    'url': title_url,
                    'channel_name': channel_name,
                    'channel_id': channel_id,
                    'time': time_str
                })
                
    except Exception as e:
        print(f"Error processing watch history: {e}")
        
    print(f"Found {len(relevant_videos)} relevant videos.")
    return relevant_videos

def process_subscriptions():
    print("Processing subscriptions...")
    relevant_channels = []
    
    try:
        with open(SUBSCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
            # Skip first line if it's header-like but csv module handles it usually if we use DictReader
            # Based on view_file, header is: チャンネル ID,チャンネルの URL,チャンネルのタイトル
            reader = csv.DictReader(f)
            
            for row in reader:
                # Adjust keys based on actual CSV header
                # The file view showed: チャンネル ID,チャンネルの URL,チャンネルのタイトル
                channel_id = row.get('チャンネル ID', '')
                channel_url = row.get('チャンネルの URL', '')
                channel_title = row.get('チャンネルのタイトル', '')
                
                if is_relevant(channel_title):
                    relevant_channels.append({
                        'channel_name': channel_title,
                        'channel_id': channel_id,
                        'channel_url': channel_url
                    })
                    
    except Exception as e:
        print(f"Error processing subscriptions: {e}")
        
    print(f"Found {len(relevant_channels)} relevant channels.")
    return relevant_channels

def save_to_csv(data, filename, fieldnames):
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def main():
    videos = process_watch_history()
    save_to_csv(videos, OUTPUT_VIDEOS_FILE, ['title', 'url', 'channel_name', 'channel_id', 'time'])
    
    channels = process_subscriptions()
    save_to_csv(channels, OUTPUT_CHANNELS_FILE, ['channel_name', 'channel_id', 'channel_url'])

if __name__ == "__main__":
    main()
