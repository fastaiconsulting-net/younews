from younews_reporter.agentic.news_reporter import NewsReportAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.agentic.generate_news_image import ImageGeneratorAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.utils import setup_logger
from younews_reporter.convert_to_html import convert_md_to_html
from datetime import datetime
import base64
import boto3
import yaml
import os
import json

from younews_reporter.utils import load_config, files_names, save_image, save_socials_post_text, save_locally, upload_to_s3

from typing import List

from __future__ import annotations
import os
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from mangum import Mangum

from lambda_helpers import get_secret

APP_NAME = os.getenv("APP_NAME", "younews-api")
app = FastAPI(title=APP_NAME, version="1.0.0")

# app.add_middleware(
#     CORSMiddleware,
# )


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": APP_NAME}


def set_args():
    # placeholder
    today = datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
    model = os.getenv("MODEL", "gpt-4.1-mini")
    resolution = os.getenv("RESOLUTION", "1920x1080")
    return today, model, resolution


@app.post("/generate-news-report")
def generate_news_report(generate_image: bool = False):

    today, model, resolution = set_args()
    # s3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'))
    logger.info("> Starting Younews Daily Report")


    logger.info("> Generating news report")
    agent = NewsReportAgent(model=model)
    response = agent.run(topics=None)
    report_txt = response.output_text

    if generate_image:
        logger.info("> Generating news image")
        agent = ImageGeneratorAgent(model=model)
        image_base64 = agent.run(report_txt, resolution)
        save_image(image_base64, image_news_report_path, logger)

    # embedd report to html
    image_path_to_embed = None
    styled_html = convert_md_to_html(
        markdown_content=report_txt,
        secondary_title=">Younews Daily Report",
        image_path_to_embed=image_path_to_embed)
    
    # generate socials post text
    logger.info("> Generating socials post text")
    agent = SocialsPostTextAgent(model=model)
    socials_post_text = agent.run(report_txt)
    save_socials_post_text(socials_post_text, socials_post_text_path, logger)


    # upload_to_s3(
    #     s3_client,
    #     today,
    #     markdown_news_report_path,
    #     html_news_report_path,
    #     image_news_report_path,
    #     socials_post_text_path,
    #     BUCKET_NAME)
    # logger.info(f"> Uploaded reports to s3://{BUCKET_NAME}")



# ------ setup -------->>
logger = setup_logger("younews-api")
handler = Mangum(app)

SECRET_NAME = os.getenv("APP_SECRET_NAME")
APP_SECRET = json.loads(get_secret(SECRET_NAME)) if SECRET_NAME else None


# ----- Local run ----->>
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)






