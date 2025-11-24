import json
import csv
from typing import Set, Dict

def extract_podcast_channels(json_path: str, output_csv_path: str):
    """
    Extracts podcast channels from watch-history.json and appends to CSV.
    """
    
    # Podcast keywords
    podcast_keywords = ["podcast", "Podcast", "PODCAST"]
    
    # Generative AI keywords for filtering
    gen_ai_keywords = [
        "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning",
        "ChatGPT", "Gemini", "LLM", "Generative AI", "GPT", "Claude", "OpenAI"
    ]

    extracted_channels: Dict[str, str] = {}  # channel_url -> channel_name

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} entries from {json_path}")

        for entry in data:
            if entry.get('header') != 'YouTube':
                continue
                
            title = entry.get('title', '')
            subtitles = entry.get('subtitles', [])
            
            # Check if title or channel name contains "podcast"
            has_podcast = any(keyword in title for keyword in podcast_keywords)
            
            if not has_podcast and subtitles:
                for subtitle in subtitles:
                    channel_name = subtitle.get('name', '')
                    if any(keyword in channel_name for keyword in podcast_keywords):
                        has_podcast = True
                        break
            
            if has_podcast:
                # Check if it's AI-related
                has_ai = any(keyword.lower() in title.lower() for keyword in gen_ai_keywords)
                
                if has_ai and subtitles:
                    for subtitle in subtitles:
                        channel_name = subtitle.get('name')
                        channel_url = subtitle.get('url')
                        
                        if channel_name and channel_url:
                            extracted_channels[channel_url] = channel_name

        print(f"Found {len(extracted_channels)} unique AI podcast channels.")

        # Read existing channels to avoid duplicates
        existing_channels = set()
        try:
            with open(output_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_channels.add(row['Channel URL'])
        except FileNotFoundError:
            pass

        # Append new channels
        new_count = 0
        with open(output_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Channel Name', 'Channel URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            for url, name in extracted_channels.items():
                if url not in existing_channels:
                    writer.writerow({'Channel Name': name, 'Channel URL': url})
                    print(f"  [ADDED] {name}")
                    new_count += 1
                else:
                    print(f"  [SKIP] {name} (already exists)")
                
        print(f"Added {new_count} new channels to {output_csv_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    json_file = "watch-history.json"
    output_file = "generative_ai_channels.csv"
    extract_podcast_channels(json_file, output_file)
