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
                model="gpt-4o-mini", # Cost-effective and capable
                messages=[
                    {"role": "system", "content": """あなたは優秀な要約アシスタントです。
提供されたYouTube動画の字幕テキストを元に、以下の構成で日本語のレポートを作成してください。

【要約】
動画の要点を600文字程度のパラグラフ形式（箇条書き不可）でまとめてください。

【考察】
動画の内容から読み取れる深い洞察や、視聴者が気づきにくい視点を提供してください。

【アクションプラン】
視聴者が明日から実践できる具体的な行動指針を3つ提案してください。
"""},
                    {"role": "user", "content": text}
                ],
                max_tokens=1000, # Increased for additional sections
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            return "要約の生成中にエラーが発生しました。"

