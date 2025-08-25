

from younews_reporter.agentic.agentic_base import AgenticBase
from openai import OpenAI
import logging


class SocialsPostTextAgent(AgenticBase):
    def __init__(self, model: str, logger: logging.Logger = None):
        super().__init__(model, logger)

    def generate_instructions(self, news_report: str, link: str = "https://fastaiconsulting-net.github.io/younews/"):
        return f"""
            You are a skilled social media copywriter.

            Write one well-crafted social media caption based on the news report below. This caption will be reused across platforms (X, LinkedIn, Instagram), so it must be:
            - Platform-neutral: not too casual, not too formal
            - Informative: the reader should understand the key facts without needing to click a link
            - Concise: no fluff, no filler — focus on the core message
            - Include 2–3 relevant hashtags (e.g., #breakingnews)
            - Optionally include 1 tasteful emoji for tone
            - Avoid clickbait. Be clear, factual, and complete in meaning.
            - Format as plain text only — no markdown, no section labels.
            - End the report with a link to the full report.

            Think of this as a 1-paragraph executive summary that also works as a post.

            ### News Report:
            \"\"\"
            {news_report}
            \"\"\"

            ### Output:
            <caption>

            🔗👉 Get the full report: {link}

            <hashtags>
        """

    def run(self, news_report: str, link: str = None):
        instructions = self.generate_instructions(news_report)

        response = self.client.responses.create(
            model=self.model,
            input=instructions,
            tools=[{"type": "web_search_preview"}],
        )

        caption = response.output_text.strip()

        if link:
            caption += f"\n\n🔗 Read more: {link}"

        self.caption = caption
        return caption


if __name__ == "__main__":
    TOPIC = "AI"
    with open(f"{TOPIC}-news-report.md") as f:
        NEWS_REPORT = f.read()

    agent = SocialsPostTextAgent(model="gpt-4.1")
    caption = agent.run(NEWS_REPORT)

    print('Caption: ', caption)
    with open(f"{TOPIC}-socials-post-text.md", "w") as f:
        f.write(caption)

    print(f"Saved response to {TOPIC}-socials-post-text.md")