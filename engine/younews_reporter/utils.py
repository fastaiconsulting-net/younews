import logging
import yaml
from datetime import datetime
import os
import boto3
import base64


def extract_main_title(markdown_content: str):
    """
    Extract the main title from markdown content.
    The main title is typically the first line that starts with # or ** and ends with **
    """
    lines = markdown_content.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Check for markdown heading (# Title)
        if line.startswith('# '):
            # Remove the # and return the title
            return line[2:]
        # Check for bold markdown (**Title**)
        elif line.startswith('**') and line.endswith('**'):
            # Remove the ** markers and return the title
            return line[2:-2]
    return "YouNews Report"  # Fallback title


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
        config['audio']['generate_audio'],
        config['audio']['voice'],
        config['audio']['model'],
        config['audio']['script_model'],
    )


def files_names(
    root_dir: str,
    s3_bucket_name: str,
    generate_image: bool = False,
    generate_audio: bool = False,
    s3_region: str = "eu-west-2"
):
    """
    base --> local path
    """
    today = datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
    base = f"{root_dir}/{today}"
    os.makedirs(base, exist_ok=True)
    markdown_news_report_path = f"{base}/news-report.md"
    html_news_report_path = f"{base}/news-report.html"
    socials_post_text_path = f"{base}/socials-post-text.txt"
    image_path = None
    image_s3_ref_path = None
    if generate_image:
        image_path = f"{base}/news-image.png"
        image_s3_ref_path = f"https://{s3_bucket_name}.s3.{s3_region}.amazonaws.com/{today}/news-image.png"
    audio_path = None
    audio_script_path = None
    audio_s3_ref_path = None
    if generate_audio:
        audio_path = f"{base}/audio.wav"
        audio_script_path = f"{base}/audio_script.txt"
        audio_s3_ref_path = f"https://{s3_bucket_name}.s3.{s3_region}.amazonaws.com/{today}/audio.wav"
    return (
        today,
        base,
        markdown_news_report_path,
        html_news_report_path,
        socials_post_text_path,
        image_path,
        image_s3_ref_path,
        audio_path,
        audio_script_path,
        audio_s3_ref_path
    )


def upload_to_s3(
    s3_client: boto3.client,
    today: str,
    main_title_path: str,
    markdown_news_report: str,
    html_news_report: str,
    image_path: str,
    socials_post_text: str,
    s3_bucket_name: str
):
    """
    s3_client.upload_file(
        FileName=file_name,
        Bucket=bucket_name,
        Key=key,
        ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/html'}
    )
    src: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """

    # save main title to file
    s3_client.upload_file(
        main_title_path,
        s3_bucket_name,
        f"{today}/main_title.txt"
    )

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
    # s3_client.upload_file(
    #     html_news_report,
    #     s3_bucket_name,
    #     "latest-news-report.html",
    #     ExtraArgs={'ContentType': 'text/html'}
    # )

    # Upload image with public read access (if exists)
    if image_path:
        s3_client.upload_file(
            image_path,
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


def save_image(image_base64, image_path, logger: logging.Logger = None):
    if logger is None:
        logger = setup_logger("younews-reporter")

    if image_base64:
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))
            logger.info(f'saved {image_path}')
        logger.info(f"> Saved image to {image_path}")
        return
    logger.info("> Image corrupt - can not saved.")


def save_socials_post_text(caption: str, location: str, logger: logging.Logger = None):
    if logger is None:
        logger = setup_logger("younews-reporter")

    with open(f"{location}", "w") as f:
        f.write(caption)
    logger.info(f"> Saved socials post text to {location}")
