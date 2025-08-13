# YouNews - AI News Subscription Platform

A modern web application for subscribing to daily AI news updates, built with a React-like frontend and DynamoDB backend.

## 🏗️ Architecture

- **Frontend**: Single-page HTML application with modern CSS and JavaScript
- **Backend**: FastAPI on AWS Lambda with DynamoDB
- **Infrastructure**: Terraform-managed AWS resources

## 📁 Project Structure

```
younews/
├── younews.html          # Main frontend application
├── config.js             # API configuration
├── setup.sh              # Setup script
├── README.md             # This file
└── DynamoDB/             # Backend API and infrastructure
    ├── app.py            # FastAPI application
    ├── subscriptions.py  # DynamoDB operations
    ├── infra/            # Terraform configuration
    └── README.md         # Backend documentation
```

## 🚀 Quick Start

### 1. Deploy the Backend

First, deploy your DynamoDB backend:

```bash
cd DynamoDB/infra
terraform init
terraform apply
```

### 2. Configure the Frontend

Run the setup script to automatically configure the API URL:

```bash
./setup.sh
```

Or manually update `config.js` with your API URL:

```javascript
const config = {
    API_BASE_URL: 'https://YOUR_API_ID.execute-api.eu-west-2.amazonaws.com',
    // ... other config
};
```

### 3. Test the Application

Open `younews.html` in your browser and test the subscription functionality.

## 🔧 API Integration

The frontend now connects directly to your DynamoDB API:

### Subscription Flow
1. User selects topics and enters email
2. Frontend calls `PUT /subscriptions` with email and topics
3. DynamoDB creates/updates subscription in both tables:
   - `subscriptions` table (PK: email, topics as String Set)
   - `topic_index` table (PK: topic, SK: email)

### Unsubscription Flow
1. User enters email to unsubscribe
2. Frontend calls `DELETE /subscriptions/{email}`
3. DynamoDB removes subscription from both tables

### Available API Endpoints
- `GET /healthz` - Health check
- `GET /subscriptions/{email}` - Get user's topics
- `PUT /subscriptions` - Create/update subscription
- `POST /subscriptions/topics:add` - Add topics to subscription
- `POST /subscriptions/topics:remove` - Remove topics from subscription
- `DELETE /subscriptions/{email}` - Delete subscription
- `GET /topics/{topic}/emails` - Get emails subscribed to a topic

## 🎨 Features

- **Modern UI**: Dark theme with purple/pink gradient accents
- **Topic Selection**: Multi-topic subscription with visual feedback
- **Real-time Updates**: Direct API integration with error handling
- **Responsive Design**: Works on desktop and mobile
- **Topic Requests**: Users can request new topics (placeholder for future enhancement)

## 🔍 Testing

### Test Subscription
1. Open `younews.html`
2. Select topics (e.g., "AI", "Machine Learning")
3. Enter your email
4. Click "Subscribe"
5. Check DynamoDB tables for the new subscription

### Test Unsubscription
1. Enter the same email
2. Click "Unsubscribe"
3. Verify the subscription is removed from DynamoDB

### API Testing
```bash
# Get API URL
cd DynamoDB/infra && terraform output -raw api_base_url

# Test health endpoint
curl -s "${BASE_URL}/healthz"

# Test subscription
curl -s -X PUT "${BASE_URL}/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","topics":["ai","ml"]}'

# Check subscription
curl -s "${BASE_URL}/subscriptions/test@example.com"

# Get emails for topic
curl -s "${BASE_URL}/topics/ai/emails"
```

## 🛠️ Development

### Adding New Topics
1. Update `config.js` with new topic mappings
2. The frontend will automatically show new topics
3. Backend will handle new topics dynamically

### Customizing the UI
- Modify CSS variables in `younews.html` for theming
- Update topic icons and descriptions in `config.js`
- Add new sections or features as needed

### Backend Modifications
- See `DynamoDB/README.md` for backend development
- API changes will require frontend updates if endpoints change

## 🔒 Security Notes

- API Gateway handles CORS and rate limiting
- Email validation is performed on both frontend and backend
- No sensitive data is stored in the frontend

## 📈 Next Steps

Potential enhancements:
- [ ] Email confirmation flow
- [ ] Topic request API endpoint
- [ ] User preferences management
- [ ] Newsletter generation and sending
- [ ] Analytics dashboard
- [ ] Admin interface for managing topics

## 🤝 Contributing

1. Test your changes thoroughly
2. Update documentation as needed
3. Ensure API compatibility
4. Test on both desktop and mobile

---

Built with ❤️ by FastAI Consulting