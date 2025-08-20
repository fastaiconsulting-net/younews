import boto3
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


DEFAULT_TOPIC_ARN = (
    "arn:aws:sns:eu-west-2:084285615195:subscriptions-api-newsletter"
)


def send_daily_email(subject: str, message: str, topic_arn: str = DEFAULT_TOPIC_ARN):
    """
    Send daily email report via AWS SNS.

    Args:
        subject: Email subject line
        message: Email body content
        topic_arn: ARN of SNS topic to publish to
    """
    try:
        logger.info("Attempting to send daily email")
        sns = boto3.client(
            'sns',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'eu-west-2')
            )
        response = sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        logger.info(f"Email sent successfully. MessageId: {response['MessageId']}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False


def draft_email(
    report_title: str = "Younews Daily by FastAI ❤️",
    path_to_report_html: str = (
        "https://younews-reports.s3.eu-west-2.amazonaws.com/"
        "2025:08:19-17:26:28/news-report.html"
    )
):
    logger.info("Drafting daily email")

    # Create the email message with HTML formatting
    message = f"""
        📰 {report_title}

        📝 Read the full report:
        {path_to_report_html}

        📰 More stories:
        https://fastaiconsulting-net.github.io/younews/

        📍 FastAI Consulting:
        https://fastaiconsulting.net

        ---
        YouNews is built with ❤️ by FastAI.
    """

    logger.info("Email draft completed")
    return message


if __name__ == "__main__":
    # Example usage
    logger.info("Starting email sending process")
    subject = "Younews Daily by FastAI ❤️"
    message = draft_email()
    send_daily_email(subject, message)
