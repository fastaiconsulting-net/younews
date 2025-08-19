

from openai import OpenAI
import base64

from younews_reporter.agentic.agentic_base import AgenticBase
import logging


class ImageGeneratorAgent(AgenticBase):
    def __init__(self, model: str, logger: logging.Logger = None):
        super().__init__(model, logger)

    def generate_prompt(self, news_report: str, resolution: str = "news_article"):
        return f"""
        Generate a ghibli style image capturing the essence of the news report below.

        ### News Report:
        {news_report}

        Resolution: {resolution}
        """

    def run(self, news_report: str, resolution: str):
        prompt = self.generate_prompt(news_report, resolution)
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            tools=[{"type": "image_generation"}],
        )
        # Save the image to a file
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]

        if image_data:
            image_base64 = image_data[0]
            return image_base64

        else:
            self.logger.error('no image data found')
            return None