from openai import OpenAI
from .logger import setup_logger

logger = setup_logger(__name__)

class Summarizer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def summarize(self, text: str) -> str:
        """
        Summarizes the given text into approximately 600 Japanese characters.
        """
        if not text:
            logger.warning("No text provided for summarization.")
            return "要約するテキストがありませんでした。"

        # Truncate text if it's extremely long to avoid token limits (though unlikely with modern models for single videos)
        # A 1 hour video speaks about 9000-10000 words. GPT-4o-mini has 128k context. We are safe.
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5.1", # Updated to GPT-5.1
                messages=[
                    {"role": "system", "content": """あなたは優秀な要約アシスタントです。
提供されたYouTube動画の字幕テキストを元に、日本語の要約を作成してください。

【要約の要件】
- 動画の要点を1000文字程度の文章でまとめてください。
- 読みやすさを重視し、意味の区切りで適宜改行を入れて、複数の段落に分けて構成してください。
- 箇条書きは使用せず、自然な文章で記述してください。
"""},
                    {"role": "user", "content": text}
                ],
                max_completion_tokens=2000, # Use max_completion_tokens for GPT-5.1
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            return "要約の生成中にエラーが発生しました。"

    def is_gen_ai_video(self, title: str, description: str) -> bool:
        """
        Determines if a video is related to Generative AI using GPT-5.1.
        """
        try:
            content = f"Title: {title}\nDescription: {description[:500]}" # Limit description length
            response = self.client.chat.completions.create(
                model="gpt-5.1", # Updated to GPT-5.1
                messages=[
                    {"role": "system", "content": """You are a strict technology content classifier.
Determine if the following video is related to the specific target topics below. Respond with 'YES' or 'NO'.

TARGET TOPICS (YES):
- Generative AI (LLM, Image Generation, AI Agents, etc.)
- Machine Learning / Deep Learning
- Robotics (Hardware, Software, Humanoids, etc.)
- Autonomous Driving / Self-driving technology
- Quantum Computing
- Semiconductors / AI Chips (NVIDIA, GPU, TPU, manufacturing, etc.)

EXCLUSION CRITERIA (NO):
- General consumer electronics reviews (Smartphones, PCs, Cameras) unless heavily focused on AI/Chips.
- General programming/web dev tutorials (HTML, CSS, basic Python) unless AI/ML related.
- General business/economy/politics unless focused on the target tech sectors.
- Entertainment/Gaming.
"""},
                    {"role": "user", "content": content}
                ],
                max_completion_tokens=50, # Increased to avoid token limit error
                temperature=0.0
            )
            result = response.choices[0].message.content.strip().upper()
            return "YES" in result
        except Exception as e:
            logger.error(f"Error during classification: {e}")
            # Default to False on error to avoid spam, or True to be safe? 
            # Let's default to False to be strict as per user request "only Gen AI".
            return False

