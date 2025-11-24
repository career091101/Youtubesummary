import csv

def extract_channel_ids_from_csv(csv_path: str, output_path: str):
    """
    Extracts channel IDs from CSV and appends to channel_ids.txt.
    """
    
    # Read existing channel IDs to avoid duplicates
    existing_ids = set()
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_ids = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        pass
    
    print(f"Found {len(existing_ids)} existing channel IDs.")
    
    # Extract channel IDs from CSV
    new_ids = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel_url = row['Channel URL']
                # Extract channel ID from URL
                if '/channel/' in channel_url:
                    channel_id = channel_url.split('/channel/')[-1]
                    if channel_id and channel_id not in existing_ids:
                        new_ids.append(channel_id)
                        existing_ids.add(channel_id)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return
    
    print(f"Found {len(new_ids)} new channel IDs to add.")
    
    # Append new IDs to file
    if new_ids:
        with open(output_path, 'a', encoding='utf-8') as f:
            for channel_id in new_ids:
                f.write(f"{channel_id}\n")
        print(f"Added {len(new_ids)} channel IDs to {output_path}")
    else:
        print("No new channel IDs to add.")

if __name__ == "__main__":
    csv_file = "generative_ai_channels.csv"
    output_file = "channel_ids.txt"
    extract_channel_ids_from_csv(csv_file, output_file)
