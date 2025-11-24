import csv
import os
import sys
import re
from typing import List, Dict
from googleapiclient.discovery import build
from src.config import Config

# Setup logger (simple print for this standalone script)
def log(msg):
    print(f"[Filter] {msg}")

def get_channel_id_from_url(url: str) -> str:
    """Extracts channel ID from URL."""
    # Expected format: https://www.youtube.com/channel/UC...
    if '/channel/' in url:
        return url.split('/channel/')[-1]
    return ""

def filter_channels(input_csv: str, output_csv: str):
    """
    Filters channels for Generative AI content using YouTube API.
    """
    if not Config.validate():
        log("Error: Missing API Key in environment variables.")
        return

    youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)

    # Keywords for Generative AI (strict)
    gen_ai_keywords = [
        "Generative AI", "生成AI", "ChatGPT", "GPT", "LLM", "Midjourney", 
        "Stable Diffusion", "Claude", "Gemini", "Copilot", "OpenAI", 
        "Anthropic", "LangChain", "RAG", "画像生成", "AI art", "Sora",
        "Large Language Model", "Llama", "Mistral"
    ]
    keyword_pattern = re.compile("|".join(map(re.escape, gen_ai_keywords)), re.IGNORECASE)

    channels_to_check = []
    
    # Read input CSV
    try:
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel_url = row['Channel URL']
                channel_id = get_channel_id_from_url(channel_url)
                if channel_id:
                    channels_to_check.append({
                        'name': row['Channel Name'],
                        'url': channel_url,
                        'id': channel_id
                    })
    except FileNotFoundError:
        log(f"Error: Input file {input_csv} not found.")
        return

    log(f"Loaded {len(channels_to_check)} channels to check.")

    filtered_channels = []
    
    # Process in batches of 50 (API limit)
    batch_size = 50
    for i in range(0, len(channels_to_check), batch_size):
        batch = channels_to_check[i:i+batch_size]
        batch_ids = [c['id'] for c in batch]
        
        try:
            response = youtube.channels().list(
                id=",".join(batch_ids),
                part="snippet"
            ).execute()
            
            for item in response.get('items', []):
                channel_id = item['id']
                snippet = item['snippet']
                title = snippet['title']
                description = snippet['description']
                
                # Find corresponding channel object
                original_channel = next((c for c in batch if c['id'] == channel_id), None)
                if not original_channel:
                    continue

                # Check for keywords in title or description
                if keyword_pattern.search(title) or keyword_pattern.search(description):
                    filtered_channels.append(original_channel)
                    log(f"  [KEEP] {title}")
                else:
                    # log(f"  [SKIP] {title}") # Too verbose
                    pass

        except Exception as e:
            log(f"Error fetching batch {i}: {e}")

    log(f"Filtered down to {len(filtered_channels)} Generative AI channels.")

    # Write output CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Channel Name', 'Channel URL']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for channel in filtered_channels:
            writer.writerow({'Channel Name': channel['name'], 'Channel URL': channel['url']})
            
    log(f"Saved results to {output_csv}")

if __name__ == "__main__":
    # Ensure we can import src
    sys.path.append(os.getcwd())
    
    input_file = "extracted_ai_channels.csv"
    output_file = "generative_ai_channels.csv"
    filter_channels(input_file, output_file)
