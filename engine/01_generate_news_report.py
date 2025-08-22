from younews_reporter.agentic.news_reporter import NewsReportAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.agentic.generate_news_image import ImageGeneratorAgent
from younews_reporter.agentic.generate_socials_post_text import SocialsPostTextAgent
from younews_reporter.utils import setup_logger, extract_main_title
import os
from younews_reporter.convert_to_html import convert_md_to_html
import boto3
from openai import OpenAI
from younews_reporter.utils import load_config, files_names, save_image, save_socials_post_text, save_locally, upload_to_s3

from news_audio.news_forecaster import AudioScript, GenerateAudio


def test_upload_to_s3_only(test_s3_only: bool = False):
    if not test_s3_only:
        return
    print('----------------------------------------------------')
    print('☠️🏴‍☠️ TESTING UPLOAD TO S3 ONLY 🏴‍☠️☠️')
    print('----------------------------------------------------')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'))
    TODAY = '2025:08:22-09:20:59'
    BUCKET_NAME = 'younews-reports'
    base = f'reports/{TODAY}'
    main_title_path = f"{base}/main_title.txt"
    markdown_news_report_path = f"{base}/news-report.md"
    html_news_report_path = f"{base}/news-report.html"
    socials_post_text_path = f"{base}/socials-post-text.txt"
    image_path = f"{base}/news-image.png"
    audio_script_path = f"{base}/audio_script.txt"
    audio_path = f"{base}/audio.wav"
    # upload to s3
    upload_to_s3(
        s3_client=s3_client,
        today=TODAY,
        main_title_path=main_title_path,
        markdown_news_report=markdown_news_report_path,
        html_news_report=html_news_report_path,
        socials_post_text=socials_post_text_path,
        image_path=image_path,
        audio_script_path=audio_script_path,
        audio_path=audio_path,
        s3_bucket_name=BUCKET_NAME
    )
    print('----------------------------------------------------')
    print('✅✅✅ TESTING UPLOAD TO S3 ONLY COMPLETED ✅✅✅')
    print('----------------------------------------------------')
    exit()


if __name__ == "__main__":
    logger = setup_logger('Topics News Engine')
    test_upload_to_s3_only(test_s3_only=False)
    TOPICS, MODEL, ROOT_DIR, GENERATE_IMAGE, RESOLUTION, BUCKET_NAME, GENERATE_AUDIO, VOICE, AUDIO_MODEL, SCRIPT_MODEL = load_config(logger=logger)
    (today,
     base,
     markdown_news_report_path,
     html_news_report_path,
     socials_post_text_path,
     image_path,
     image_s3_ref_path,
     audio_path,
     audio_script_path,
     audio_s3_ref_path) = files_names(ROOT_DIR, BUCKET_NAME, GENERATE_IMAGE, GENERATE_AUDIO)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'))
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    logger.info("> Starting Younews Daily Report")
    # generate news report
    agent = NewsReportAgent(model=MODEL)
    response = agent.run(topics=TOPICS)
    report_txt = response.output_text
    main_title = extract_main_title(report_txt)

    # generate image
    if GENERATE_IMAGE:
        agent = ImageGeneratorAgent(model=MODEL)
        image_base64 = agent.run(report_txt, RESOLUTION)
        save_image(image_base64, image_path, logger)

    if GENERATE_AUDIO:
        script = AudioScript.generate_audio_script(client, main_title, report_txt, SCRIPT_MODEL)
        AudioScript.save_script(script, audio_script_path)
        audio_generator = GenerateAudio(client=client, voice=VOICE, model=AUDIO_MODEL)
        audio_generator.generate_audio(script, audio_path)
        logger.info(f"> Saved audio to {audio_path}")
        logger.info(f"> Saved audio script to {audio_script_path}")

    # html report: local reference
    styled_html = convert_md_to_html(
        markdown_content=report_txt,
        secondary_title=">Younews Daily Report",
        image_path_to_embed=image_s3_ref_path,
        embed_audio_file=audio_s3_ref_path)
    
    # generate socials post text
    agent = SocialsPostTextAgent(model=MODEL)
    socials_post_text = agent.run(report_txt)
    save_socials_post_text(socials_post_text, socials_post_text_path, logger)

    save_locally(markdown_news_report_path, report_txt, html_news_report_path, styled_html, logger)
    logger.info(f"> Saved reports to {ROOT_DIR}/{today}-[files]")

    # save main title to file
    main_title_path = f"{base}/main_title.txt"
    with open(main_title_path, "w") as f:
        f.write(main_title)

    # upload to s3
    upload_to_s3(
        s3_client=s3_client,
        today=today,
        main_title_path=main_title_path,
        markdown_news_report=markdown_news_report_path,
        html_news_report=html_news_report_path,
        socials_post_text=socials_post_text_path,
        image_path=image_path,
        audio_script_path=audio_script_path,
        audio_path=audio_path,
        s3_bucket_name=BUCKET_NAME
    )
    logger.info(f"> Uploaded reports to s3://{BUCKET_NAME}/{today}")

    # open image
    # os.system(f"open {html_news_report_path}")