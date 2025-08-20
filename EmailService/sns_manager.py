from __future__ import annotations
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict
import json

# Config (envs or defaults)
REGION = os.getenv("AWS_REGION", "eu-west-2")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

sns = boto3.client("sns", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)

class NewsletterManager:
    def __init__(self):
        self.topic_arn = SNS_TOPIC_ARN
        self.queue_url = SQS_QUEUE_URL

    def subscribe(self, email: str) -> Dict:
        """
        Subscribe an email to the newsletter.
        This will trigger a confirmation email to the subscriber.
        """
        try:
            response = sns.subscribe(
                TopicArn=self.topic_arn,
                Protocol="email",
                Endpoint=email,
                ReturnSubscriptionArn=True
            )
            return {
                "success": True,
                "message": "Confirmation email sent. Please check your inbox.",
                "subscription_arn": response["SubscriptionArn"]
            }
        except ClientError as e:
            return {
                "success": False,
                "message": str(e)
            }

    def unsubscribe(self, subscription_arn: str) -> Dict:
        """
        Unsubscribe using the subscription ARN.
        Note: Users can also unsubscribe directly via the link in emails.
        """
        try:
            sns.unsubscribe(
                SubscriptionArn=subscription_arn
            )
            return {
                "success": True,
                "message": "Successfully unsubscribed"
            }
        except ClientError as e:
            return {
                "success": False,
                "message": str(e)
            }

    def get_subscriptions(self) -> List[Dict]:
        """
        Get all subscriptions for the topic.
        Only returns confirmed subscriptions.
        """
        try:
            paginator = sns.get_paginator('list_subscriptions_by_topic')
            subscriptions = []
            
            for page in paginator.paginate(TopicArn=self.topic_arn):
                for sub in page['Subscriptions']:
                    if sub['SubscriptionArn'] != 'PendingConfirmation':
                        subscriptions.append({
                            'email': sub['Endpoint'],
                            'subscription_arn': sub['SubscriptionArn'],
                            'status': 'subscribed'
                        })
            
            return subscriptions
        except ClientError as e:
            print(f"Error getting subscriptions: {e}")
            return []

    def get_subscription_by_email(self, email: str) -> Optional[Dict]:
        """
        Find a subscription by email address.
        Returns None if not found or not confirmed.
        """
        subscriptions = self.get_subscriptions()
        for sub in subscriptions:
            if sub['email'] == email:
                return sub
        return None

    def publish_message(self, message: str, subject: str = None) -> Dict:
        """
        Publish a message to all subscribers
        """
        try:
            publish_args = {
                "TopicArn": self.topic_arn,
                "Message": message
            }
            if subject:
                publish_args["Subject"] = subject

            response = sns.publish(**publish_args)
            return {
                "success": True,
                "message_id": response["MessageId"]
            }
        except ClientError as e:
            return {
                "success": False,
                "message": str(e)
            }

    def customize_subscription_message(self, email: str) -> Dict:
        """
        Customize the subscription message when publishing
        """
        return {
            "default": json.dumps({
                "type": "subscription_welcome",
                "email": email
            }),
            "email": f"""
            <h1>Welcome to YouNews!</h1>
            
            Thank you for subscribing to our newsletter. You'll receive:
                        <ul>
                            <li>Daily AI-generated news summaries</li>
                            <li>Market insights</li>
                            <li>Tech updates</li>
                        </ul>

            You can unsubscribe at any time using the unsubscribe link in our emails.

            Best regards,
            YouNews Team
            """
        }

    def publish_welcome_message(self, email: str) -> Dict:
        try:
            response = sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps(self.customize_subscription_message(email)),
                MessageStructure='json',
                Subject="Welcome to YouNews!"
            )
            return {
                "success": True,
                "message_id": response["MessageId"]
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e)
            }

# Initialize the manager
newsletter = NewsletterManager()

if __name__ == "__main__":
    # Example usage
    email = "test@example.com"
    
    # Subscribe
    result = newsletter.subscribe(email)
    print(f"Subscription result: {result}")
    
    # Get subscriptions
    subs = newsletter.get_subscriptions()
    print(f"Current subscriptions: {subs}")
    
    # Publish test message
    msg_result = newsletter.publish_message(
        "Hello subscribers!",
        "Test Message"
    )
    print(f"Message publish result: {msg_result}")
