import json
import csv
from typing import Set, Dict

def extract_vc_channels(json_path: str, output_csv_path: str):
    """
    Extracts venture capital channels from watch-history.json and appends to CSV.
    """
    
    # Known VC channel names and keywords
    vc_keywords = [
        "a16z", "Andreessen Horowitz", "Y Combinator", "Sequoia", 
        "Greylock", "Accel", "Benchmark", "Kleiner Perkins",
        "Lightspeed", "Index Ventures", "General Catalyst",
        "Founders Fund", "Redpoint", "NEA", "Bessemer",
        "Khosla Ventures", "First Round", "500 Startups",
        "Techstars", "Initialized Capital"
    ]

    extracted_channels: Dict[str, str] = {}  # channel_url -> channel_name

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} entries from {json_path}")

        for entry in data:
            if entry.get('header') != 'YouTube':
                continue
                
            subtitles = entry.get('subtitles', [])
            
            if subtitles:
                for subtitle in subtitles:
                    channel_name = subtitle.get('name', '')
                    channel_url = subtitle.get('url')
                    
                    # Check if channel name contains VC keywords
                    if any(keyword.lower() in channel_name.lower() for keyword in vc_keywords):
                        if channel_name and channel_url:
                            extracted_channels[channel_url] = channel_name

        print(f"Found {len(extracted_channels)} unique VC channels.")

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
                
        print(f"Added {new_count} new VC channels to {output_csv_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    json_file = "watch-history.json"
    output_file = "generative_ai_channels.csv"
    extract_vc_channels(json_file, output_file)
