// YouNews API Configuration
// Update this file with your deployed API URL from Terraform

const config = {
    // Replace this with your actual API URL from terraform output
    // Run: cd DynamoDB/infra && terraform output -raw api_base_url
    // API_BASE_URL: 'https://oorqz471eg.execute-api.eu-west-2.amazonaws.com',
    API_BASE_URL: 'https://8a17q933pb.execute-api.eu-west-2.amazonaws.com',

    
    // Available topics for the frontend
    AVAILABLE_TOPICS: {
        'us-politics': '🗽 US Politics',
        'global-politics': '🌍 Global Politics',
        'economics': '💰 Economics',
        'ai': '🤖 AI',
        'machine-learning': '🧠 Machine Learning',
        'technology': '💻 Technology',
        'football': '⚽ Football',
        'us-sports': '🏈 US Sports',
        'trump': '🇺🇸 Trump',
        'us-stocks': '📈 US Stocks',
        'eurozone-stocks': '📊 Eurozone Stocks',
        'south-african-stocks': '🇿🇦 South African Stocks',
        'us-dollar': '💵 US Dollar',
        'eu': '🇪🇺 EU',
        'uk': '🇬🇧 UK',
        'china': '🇨🇳 China',
        'south-africa': '🇿🇦 South Africa'
    }
};

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = config;
} else {
    window.YouNewsConfig = config;
}
