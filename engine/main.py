from younews_reporter.agentic.news_reporter import NewsReportAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.agentic.generate_news_image import ImageGeneratorAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.utils import setup_logger
import os
from younews_reporter.convert_to_html import convert_md_to_html
import boto3

from younews_reporter.utils import load_config, files_names, save_image, save_socials_post_text, save_locally, upload_to_s3






if __name__ == "__main__":
    TOPICS, MODEL, ROOT_DIR, GENERATE_IMAGE, RESOLUTION, BUCKET_NAME = load_config()
    (today,
     markdown_news_report_path,
     html_news_report_path,
     socials_post_text_path,
     image_news_report_path,
     image_reference_path,
     image_s3_url) = files_names(ROOT_DIR, BUCKET_NAME, GENERATE_IMAGE)
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
        image_base64 = agent.run(report_txt, RESOLUTION)
        save_image(image_base64, image_news_report_path, logger)

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
    save_socials_post_text(socials_post_text, socials_post_text_path, logger)

    save_locally(markdown_news_report_path, report_txt, html_news_report_path, local_html, logger)
    logger.info(f"> Saved reports to {ROOT_DIR}/{today}-[files]")

    # upload to s3
    upload_to_s3(
        s3_client,
        today,
        markdown_news_report_path,
        html_news_report_path,
        image_news_report_path,
        socials_post_text_path,
        BUCKET_NAME)
    logger.info(f"> Uploaded reports to s3://{BUCKET_NAME}")

    # open image
    os.system(f"open {html_news_report_path}")