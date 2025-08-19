import logging
import yaml
from datetime import datetime

import boto3
import base64


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


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


def files_names(
    root_dir: str,
    s3_bucket_name: str,
    generate_image: bool = False):
    today = datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
    markdown_news_report_path = f"{root_dir}/{today}-news-report.md"
    html_news_report_path = f"{root_dir}/{today}-news-report.html"
    socials_post_text_path = f"{root_dir}/{today}-socials-post-text.txt"
    image_news_report_path = None
    image_reference_path = None
    image_s3_url = None
    if generate_image:
        image_reference_path = f"{today}-news-image.png"
        image_news_report_path = f"{root_dir}/{image_reference_path}"
        image_s3_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{today}/news-image.png"
    else:
        image_news_report_path = None
        image_reference_path = None
    return today, markdown_news_report_path, html_news_report_path, socials_post_text_path, image_news_report_path, image_reference_path, image_s3_url


def upload_to_s3(
    s3_client: boto3.client,
    today: str,
    markdown_news_report: str,
    html_news_report: str,
    image_news_report: str,
    socials_post_text: str,
    s3_bucket_name: str):
    """
    s3_client.upload_file(
        FileName=file_name,
        Bucket=bucket_name,
        Key=key,
        ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/html'}
    )
    src: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """

    # Upload markdown report (private)
    s3_client.upload_file(markdown_news_report, s3_bucket_name, f"{today}/news-report.md")
    
    # Upload HTML report with public read access
    s3_client.upload_file(
        html_news_report,
        s3_bucket_name,
        f"{today}/news-report.html",
        ExtraArgs={'ContentType': 'text/html'}
    )

    # overwrite <Todays> news
    s3_client.upload_file(
        html_news_report,
        s3_bucket_name,
        f"latest-news-report.html",
        ExtraArgs={'ContentType': 'text/html'}
    )

    
    # Upload image with public read access (if exists)
    if image_news_report:
        s3_client.upload_file(
            image_news_report, 
            s3_bucket_name, 
            f"{today}/news-image.png",
            ExtraArgs={'ContentType': 'image/png'}
        )
        # overwrite <Todays> news: not implemented! Change reference inside image.
        # s3_client.upload_file(
        #     image_news_report,
        #     BUCKET_NAME,
        #     "latest-news-image.png",
        #     ExtraArgs={'ContentType': 'image/png'}
        # )
    
    # Upload socials post text
    s3_client.upload_file(socials_post_text, s3_bucket_name, f"{today}/socials-post-text.txt")


def save_locally(
    markdown_news_report: str,
    report_txt: str,
    html_file_path: str,
    local_html: str,
    logger: logging.Logger = None
):
    
    if logger is None:
        logger = setup_logger("younews-reporter")

    # markdown report
    with open(markdown_news_report, "w") as f:
        f.write(report_txt)
    logger.info(f"> Saved markdown report to {markdown_news_report}")

    # Save local html to file
    with open(html_file_path, "w") as html_file:
        html_file.write(local_html)
    logger.info(f"> Saved HTML report to {html_file_path}")


def save_image(image_base64, image_news_report, logger: logging.Logger = None):
    if logger is None:
        logger = setup_logger("younews-reporter")

    if image_base64:
        with open(image_news_report, "wb") as f:
            f.write(base64.b64decode(image_base64))
            logger.info(f'saved {image_news_report}')
        logger.info(f"> Saved image to {image_news_report}")
        return
    logger.info("> Image corrupt - can not saved.")


def save_socials_post_text(caption: str, location: str, logger: logging.Logger = None):
    if logger is None:
        logger = setup_logger("younews-reporter")

    with open(f"{location}", "w") as f:
        f.write(caption)
    logger.info(f"> Saved socials post text to {location}")
