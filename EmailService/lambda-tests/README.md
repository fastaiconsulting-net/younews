# Lambda Test Events

This directory contains test events for AWS Lambda testing. These events simulate API Gateway v2 HTTP API requests.

## Available Tests

1. `health-check.json` - Test the health check endpoint
2. `subscribe.json` - Test subscribing a new email
3. `get-subscription.json` - Test getting subscription status for an email
4. `unsubscribe.json` - Test unsubscribing using subscription ARN
5. `get-all-subscriptions.json` - Test getting all confirmed subscriptions

## How to Use

1. Go to AWS Lambda Console
2. Select your function
3. Go to "Test" tab
4. Click "Create new event"
5. Give it a name (e.g., "SubscribeTest")
6. Copy and paste the contents of the desired test file
7. Click "Save"
8. Click "Test" to run

## Notes

- For `subscribe.json`, replace `test@example.com` with a real email to test actual confirmation emails
- For `unsubscribe.json`, replace the example ARN with a real subscription ARN
- All tests include CORS headers since the API has CORS enabled
- Tests use API Gateway v2 payload format version 2.0
