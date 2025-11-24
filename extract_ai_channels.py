import json
import csv
import re
from typing import Set, Dict, Tuple

def extract_ai_channels(json_path: str, output_csv_path: str):
    """
    Extracts AI-related channels from watch-history.json and saves them to a CSV file.
    """
    
    # Keywords to identify AI-related content
    ai_keywords = [
        "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", 
        "Neural Network", "ChatGPT", "Gemini", "LLM", "Generative AI", "GPT", 
        "Midjourney", "Stable Diffusion", "Claude", "Llama", "Copilot", 
        "OpenAI", "Google DeepMind", "Anthropic", "Mistral", "Hugging Face"
    ]
    
    # Compile regex for faster matching (case-insensitive)
    keyword_pattern = re.compile("|".join(map(re.escape, ai_keywords)), re.IGNORECASE)

    extracted_channels: Dict[str, str] = {} # channel_url -> channel_name

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} entries from {json_path}")

        for entry in data:
            # Check if it's a YouTube video entry
            if entry.get('header') != 'YouTube':
                continue
                
            title = entry.get('title', '')
            subtitles = entry.get('subtitles', [])
            
            # Check if title contains AI keywords
            if keyword_pattern.search(title):
                if subtitles:
                    for subtitle in subtitles:
                        channel_name = subtitle.get('name')
                        channel_url = subtitle.get('url')
                        
                        if channel_name and channel_url:
                            extracted_channels[channel_url] = channel_name

        print(f"Found {len(extracted_channels)} unique AI-related channels.")

        # Write to CSV
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Channel Name', 'Channel URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for url, name in extracted_channels.items():
                writer.writerow({'Channel Name': name, 'Channel URL': url})
                
        print(f"Successfully saved extracted channels to {output_csv_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    json_file = "watch-history.json"
    output_file = "extracted_ai_channels.csv"
    extract_ai_channels(json_file, output_file)
