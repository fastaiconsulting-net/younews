#!/bin/bash

# YouNews Setup Script
# This script helps you configure the API URL for the frontend

echo "🚀 YouNews Setup Script"
echo "========================"

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found in current directory"
    echo "Please run this script from the root of your YouNews project"
    exit 1
fi

# Check if DynamoDB directory exists
if [ ! -d "DynamoDB" ]; then
    echo "❌ Error: DynamoDB directory not found"
    echo "Please make sure your DynamoDB backend is in the DynamoDB/ directory"
    exit 1
fi

echo "📋 Checking Terraform outputs..."

# Try to get the API URL from Terraform
if [ -d "DynamoDB/infra" ]; then
    cd DynamoDB/infra
    
    # Check if terraform state exists
    if [ -f "terraform.tfstate" ]; then
        echo "✅ Found Terraform state, getting API URL..."
        API_URL=$(terraform output -raw api_base_url 2>/dev/null)
        
        if [ $? -eq 0 ] && [ ! -z "$API_URL" ]; then
            echo "✅ Found API URL: $API_URL"
            
            # Go back to root directory
            cd ../..
            
            # Update config.js
            echo "📝 Updating config.js with API URL..."
            sed -i.bak "s|API_BASE_URL: 'https://YOUR_API_ID.execute-api.eu-west-2.amazonaws.com'|API_BASE_URL: '$API_URL'|" config.js
            
            echo "✅ Configuration updated successfully!"
            echo ""
            echo "🎉 Setup complete! You can now:"
            echo "1. Open index.html in your browser"
            echo "2. Test the subscription functionality"
            echo "3. Check your DynamoDB tables for new subscriptions"
            
        else
            echo "❌ Could not get API URL from Terraform"
            echo "Make sure your infrastructure is deployed:"
            echo "  cd DynamoDB/infra && terraform apply"
        fi
    else
        echo "❌ No Terraform state found"
        echo "Please deploy your infrastructure first:"
        echo "  cd DynamoDB/infra && terraform apply"
    fi
    
    cd ../..
else
    echo "❌ DynamoDB/infra directory not found"
    echo "Please make sure your Terraform files are in DynamoDB/infra/"
fi

echo ""
echo "📚 Next steps:"
echo "1. Deploy your DynamoDB backend if not already done"
echo "2. Update config.js with your API URL manually if needed"
echo "3. Test the frontend by opening index.html"
echo "4. Check your DynamoDB tables for subscriptions"
