#!/bin/bash

# Environment Variables Configuration:
# Create a .env file in the project root with the following variables:
#
# Application Settings:
# GITHUB_PAGES_URL - URL of your GitHub Pages site
# VIRTUAL_ENV_PATH - Path to your virtual environment
# GENERATE_NEWS - Set to true/false to enable/disable news generation
# OPEN_IN_BROWSER - Set to true/false to automatically open the site after deployment
#
# AWS Credentials:
# AWS_ACCESS_KEY_ID - Your AWS access key
# AWS_SECRET_ACCESS_KEY - Your AWS secret key
# AWS_DEFAULT_REGION - Your AWS region (e.g., us-east-1)
#

# Load environment variables from .env file
load_env() {
    if [ -f ".env" ]; then
        echo "📝 Loading environment variables from .env..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "⚠️  No .env file found, using default values..."
    fi
}

log_env() {
    echo "🔍 Environment variables:"
    echo "====================== OpenAI API Key =========================="
    echo "OPENAI_API_KEY: $OPENAI_API_KEY"
    echo "===================== AWS Credentials =========================="
    echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
    echo "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY"
    echo "AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"
    echo "===================== Application Settings ====================="
    echo "GITHUB_PAGES_URL: $GITHUB_PAGES_URL"
    echo "VIRTUAL_ENV_PATH: $VIRTUAL_ENV_PATH"
    echo "GENERATE_NEWS: $GENERATE_NEWS"
    echo "OPEN_IN_BROWSER: $OPEN_IN_BROWSER"
    echo "================================================================"
}


verify_aws_credentials() {
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        echo "❌ Error: AWS credentials not found in .env file"
        echo "Please create a .env file with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        exit 1
    fi
}

verify_openai_api_key() {
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ Error: OpenAI API key not found in .env file"
        echo "Please create a .env file with OPENAI_API_KEY"
        exit 1
    fi
}

delete_old_index_html() {
    echo "🗑️ Deleting old index.html..."
    rm index.html
}

change_to_engine_directory() {
    echo "📂 Changing to Engine directory..."
    cd Engine
}

activate_virtual_environment() {
    # Activate virtual environment if it exists
    if [ -d "${VIRTUAL_ENV_PATH}" ]; then
        echo "🔮 Activating virtual environment..."
        source "${VIRTUAL_ENV_PATH}/bin/activate"
    fi
}

generate_news_and_push_to_s3() {
    echo "📰🔄 Generating today's news report & pushing to s3..."
    if [ "${GENERATE_NEWS}" = true ]; then
        python 01_generate_news_report.py
        if [ $? -ne 0 ]; then
            echo "❌ News generation failed! Exiting..."
            exit 1
        fi
    else
        echo "🦠 Skipping news generation..."
    fi
}

generate_html() {
    echo "🌐 Building HTML documentation..."
    python 02_generate_home_page_html.py
    if [ $? -ne 0 ]; then
        echo "❌ HTML generation failed! Exiting..."
        exit 1
    fi
}

push_to_github() {
    echo "🔄 Pushing to github..."
    cd ..
    git add .
    git commit -m "Daily deployment $(date +%Y:%m:%d-%H:%M:%S)"
    git push
    if [ $? -ne 0 ]; then
        echo "❌ Git push failed! Exiting..."
        exit 1
    fi

}

open_in_browser() {
    if [ "${OPEN_IN_BROWSER}" = true ]; then
        echo "🔗 Opening site in browser..."
        open "${GITHUB_PAGES_URL}"
        # echo "🔍 Opening generated HTML page..."
        # cd ..
        # open index.html
    fi
}

send_email_to_subscribers() {
    echo "💌 Sending email..."
    python Engine/03_email_daily_sns.py
}

deactivate_venv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "👋 Deactivating virtual environment..."
        deactivate
    fi
}

main() {
    clear
    echo "🚀 Starting YouNews daily deployment..."
    cd /Users/zachwolpe/Documents/build/younews
    load_env
    log_env
    verify_aws_credentials
    verify_openai_api_key
    delete_old_index_html
    change_to_engine_directory
    activate_virtual_environment
    generate_news_and_push_to_s3
    generate_html
    push_to_github
    open_in_browser
    send_email_to_subscribers
    deactivate_venv
    echo "✨ Daily deployment completed successfully!"
}



main






