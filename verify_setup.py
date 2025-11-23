import sys
import os

def check_file(path):
    if os.path.exists(path):
        print(f"[OK] File exists: {path}")
    else:
        print(f"[FAIL] File missing: {path}")
        return False
    return True

def check_imports():
    try:
        import googleapiclient
        import youtube_transcript_api
        import openai
        import dotenv
        print("[OK] All dependencies installed.")
    except ImportError as e:
        print(f"[FAIL] Dependency missing: {e}")
        return False
    
    # Check internal imports by adding src to path
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    try:
        from youtube_client import YouTubeClient
        from summarizer import Summarizer
        from email_sender import EmailSender
        print("[OK] Internal modules imported successfully.")
    except ImportError as e:
        print(f"[FAIL] Internal module import error: {e}")
        return False
    return True

def main():
    print("Verifying project setup...")
    
    files_to_check = [
        'requirements.txt',
        '.env.example',
        '.github/workflows/daily_summary.yml',
        'src/main.py',
        'src/youtube_client.py',
        'src/summarizer.py',
        'src/email_sender.py'
    ]
    
    all_files_exist = all([check_file(f) for f in files_to_check])
    
    if not all_files_exist:
        print("Some files are missing.")
        sys.exit(1)
        
    if not check_imports():
        print("Import checks failed. Did you install requirements?")
        sys.exit(1)
        
    print("\nVerification successful! The project structure and code are ready.")
    print("To run the actual application, you need to:")
    print("1. Create a .env file with your API keys.")
    print("2. Run 'python src/main.py'")

if __name__ == "__main__":
    main()
