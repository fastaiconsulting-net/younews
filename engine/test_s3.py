from younews_reporter.agentic.news_reporter import NewsReportAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.agentic.generate_news_image import ImageGeneratorAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.utils import setup_logger
import os
import yaml
from datetime import datetime
from younews_reporter.convert_to_html import convert_md_to_html
import boto3
import base64


def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return (
        config['topics'],
        config['model'],
        config['output']['root'],
        config['img']['generate_image'],
        config['img']['resolution'],
        config['s3']['bucket_name'],
    )




if __name__ == "__main__":
    TOPICS, MODEL, ROOT_DIR, GENERATE_IMAGE, RESOLUTION, BUCKET_NAME = load_config()
    # LOAD FILES
    S3_root = f"{BUCKET_NAME}/2025:08:15-11:10:38/"
    today = "2025:08:15-10:59:14"
    SOCIALS_POST_TEXT_PATH = f"reports/{today}-socials-post-text.txt"
    HTML_NEWS_REPORT_PATH = f"reports/{today}-news-report.html"
    MARKDOWN_NEWS_REPORT_PATH = f"reports/{today}-news-report.md"
    IMAGE_NEWS_REPORT_PATH = f"reports/{today}-news-image.png"    

    # file names
    socials_post_text_name = "socials-post-text.txt"
    html_news_report_name = "news-report.html"
    image_news_report_name = "news-image.png"

    logger = setup_logger('Topics News Engine')

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'))


    # load files
    # with open(SOCIALS_POST_TEXT_PATH, 'r') as f:
    #     socials_post_text = f.read()
    # with open(HTML_NEWS_REPORT_PATH, 'r') as f:
    #     html_news_report = f.read()
    # with open(MARKDOWN_NEWS_REPORT_PATH, 'r') as f:
    #     markdown_news_report = f.read()
    # with open(IMAGE_NEWS_REPORT_PATH, 'rb') as f:
    #     image_news_report = f.read()

    print('s3_client.upload_file:')

    # print('----------------------- markdown_news_report: ')
    # print(markdown_news_report)
    # print('----------------------- html_news_report: ')
    # print(html_news_report) 
    # print('----------------------- image_news_report: ')
    # print(image_news_report)
    # print('----------------------- socials_post_text: ')
    # print(socials_post_text)

    # upload to s3
    upload_to_s3(
        s3_client,
        today=today,
        markdown_news_report=MARKDOWN_NEWS_REPORT_PATH,
        socials_post_text=SOCIALS_POST_TEXT_PATH,
        html_news_report=HTML_NEWS_REPORT_PATH,
        image_news_report=IMAGE_NEWS_REPORT_PATH)

    logger.info(f"> Uploaded reports to s3://{BUCKET_NAME}")

    # open image