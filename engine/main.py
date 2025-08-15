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


def files_names(generate_image: bool = False):
    today = datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
    markdown_news_report_path = f"{ROOT_DIR}/{today}-news-report.md"
    html_news_report_path = f"{ROOT_DIR}/{today}-news-report.html"
    socials_post_text_path = f"{ROOT_DIR}/{today}-socials-post-text.txt"
    image_news_report_path = None
    image_reference_path = None
    image_s3_url = None
    if generate_image:
        image_reference_path = f"{today}-news-image.png"
        image_news_report_path = f"{ROOT_DIR}/{image_reference_path}"
        image_s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{today}/news-image.png"
    else:
        image_news_report_path = None
        image_reference_path = None
    return today, markdown_news_report_path, html_news_report_path, socials_post_text_path, image_news_report_path, image_reference_path, image_s3_url


def upload_to_s3(s3_client: boto3.client, today: str, markdown_news_report: str,
                 html_news_report: str, image_news_report: str, socials_post_text: str):
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
    s3_client.upload_file(markdown_news_report, BUCKET_NAME, f"{today}/news-report.md")
    
    # Upload HTML report with public read access
    s3_client.upload_file(
        html_news_report,
        BUCKET_NAME,
        f"{today}/news-report.html",
        ExtraArgs={'ContentType': 'text/html'}
    )

    # overwrite <Todays> news
    s3_client.upload_file(
        html_news_report,
        BUCKET_NAME,
        f"latest-news-report.html",
        ExtraArgs={'ContentType': 'text/html'}
    )

    
    # Upload image with public read access (if exists)
    if image_news_report:
        s3_client.upload_file(
            image_news_report, 
            BUCKET_NAME, 
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
    s3_client.upload_file(socials_post_text, BUCKET_NAME, f"{today}/socials-post-text.txt")


def upload_to_ssdfsdsgsfd3(s3_client: boto3.client, today: str, markdown_news_report: str,
                 html_news_report: str, image_news_report: str, socials_post_text: str):
    # Upload markdown report (private)
    s3_client.upload_file(markdown_news_report, BUCKET_NAME, f"{today}/news-report.md")
    
    # Upload HTML report with public read access
    s3_client.upload_file(
        html_news_report, 
        BUCKET_NAME, 
        f"{today}/news-report.html",
        ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/html'}
    )
    
    # Upload image with public read access (if exists)
    if image_news_report:
        s3_client.upload_file(
            image_news_report, 
            BUCKET_NAME, 
            f"{today}/news-image.png",
            ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'}
        )
    
    # Upload socials post text (private)
    s3_client.upload_file(socials_post_text, BUCKET_NAME, f"{today}/socials-post-text.txt")


def save_locally(markdown_news_report: str, report_txt: str, html_file_path: str, local_html: str):
    # markdown report
    with open(markdown_news_report, "w") as f:
        f.write(report_txt)
    logger.info(f"> Saved markdown report to {markdown_news_report}")

    # Save local html to file
    with open(html_file_path, "w") as html_file:
        html_file.write(local_html)
    logger.info(f"> Saved HTML report to {html_file_path}")


def save_image(image_base64, image_news_report):
    if image_base64:
        with open(image_news_report, "wb") as f:
            f.write(base64.b64decode(image_base64))
            logger.info(f'saved {image_news_report}')
        logger.info(f"> Saved image to {image_news_report}")
        return
    logger.info("> Image corrupt - can not saved.")


def save_socials_post_text(caption: str, location: str):
    with open(f"{location}", "w") as f:
        f.write(caption)
    logger.info(f"> Saved socials post text to {location}")


if __name__ == "__main__":
    TOPICS, MODEL, ROOT_DIR, GENERATE_IMAGE, RESOLUTION, BUCKET_NAME = load_config()
    (today,
     markdown_news_report_path,
     html_news_report_path,
     socials_post_text_path,
     image_news_report_path,
     image_reference_path,
     image_s3_url) = files_names(GENERATE_IMAGE)
    logger = setup_logger('Topics News Engine')

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'))

    logger.info("> Starting Younews Daily Report")
    # generate news report
    agent = NewsReportAgent(model=MODEL)
    response = agent.run(topics=TOPICS)
    report_txt = response.output_text

    # generate image
    if GENERATE_IMAGE:
        agent = ImageGeneratorAgent(model=MODEL)
        image_base64 = agent.run(report_txt, image_news_report_path, RESOLUTION)
        save_image(image_base64, image_news_report_path)

    # embedd report to html
    styled_html = convert_md_to_html(
        markdown_content=report_txt,
        secondary_title=">Younews Daily Report",
        image_path_to_embed=image_s3_url)
    local_html = convert_md_to_html(
        markdown_content=report_txt,
        secondary_title=">Younews Daily Report",
        image_path_to_embed=image_reference_path)
    


    # generate socials post text
    agent = SocialsPostTextAgent(model=MODEL)
    socials_post_text = agent.run(report_txt)
    save_socials_post_text(socials_post_text, socials_post_text_path)

    save_locally(markdown_news_report_path, report_txt, html_news_report_path, local_html)
    logger.info(f"> Saved reports to {ROOT_DIR}/{today}-[files]")

    # upload to s3
    upload_to_s3(
        s3_client,
        today,
        markdown_news_report_path,
        html_news_report_path,
        image_news_report_path,
        socials_post_text_path)
    logger.info(f"> Uploaded reports to s3://{BUCKET_NAME}")

    # open image
    os.system(f"open {html_news_report_path}")