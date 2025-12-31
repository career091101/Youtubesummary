import os
import sys
from src.summarizer import Summarizer
from src.config import Config

def test_filter():
    api_key = Config.OPENAI_API_KEY
    if not api_key:
        print("Error: OPENAI_API_KEY not found.")
        return

    summarizer = Summarizer(api_key)

    test_cases = [
        # Should be YES
        ("New Humanoid Robot from Tesla", "Tesla Optimus Gen 2 update..."),
        ("NVIDIA Blackwell Chip Architecture Explained", "Deep dive into the new B200 GPU..."),
        ("Quantum Error Correction Breakthrough", "Google Quantum AI team announces..."),
        ("Waymo expands to Los Angeles", "Autonomous driving service now available..."),
        ("ChatGPT vs Claude 3.5 Sonnet", "Comparison of top LLMs..."),
        ("TSMC 2nm Process Technology", "Semiconductor manufacturing update..."),
        
        # Should be NO
        ("iPhone 16 Review: Best Camera Ever?", "Reviewing the new iPhone features..."),
        ("Python for Beginners: Variables and Loops", "Learn the basics of Python programming..."),
        ("Toyota Financial Results 2024", "Annual earnings report..."),
        ("Elden Ring Shadow of the Erdtree Gameplay", "Playing the new DLC..."),
        ("How to build a gaming PC", "Selecting parts for a gaming rig..."),
        ("Top 10 Travel Destinations in Japan", "Best places to visit..."),
        
        # Borderline (Should likely be NO based on strictness, or YES if very specific)
        ("New MacBook Pro M4 Chip", "Apple's new silicon..."), # Borderline: Chip related but consumer product
    ]

    print(f"{'Title':<50} | {'Expected':<10} | {'Actual':<10} | {'Result'}")
    print("-" * 85)

    for title, description in test_cases:
        is_ai = summarizer.is_gen_ai_video(title, description)
        actual = "YES" if is_ai else "NO"
        
        # Simple expectation logic for this test script
        expected = "YES"
        if "iPhone" in title or "Python" in title or "Toyota" in title or "Elden Ring" in title or "gaming PC" in title or "Travel" in title:
            expected = "NO"
        if "MacBook" in title:
             expected = "NO" # Expecting strict filter to exclude consumer chips unless explicitly AI focused

        result = "PASS" if actual == expected else "FAIL"
        print(f"{title[:47]:<50} | {expected:<10} | {actual:<10} | {result}")

if __name__ == "__main__":
    test_filter()
