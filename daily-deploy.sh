#!/bin/bash

clear
echo "🚀 Starting YouNews daily deployment..."

echo "📂 Changing to Engine directory..."
cd Engine

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔮 Activating virtual environment..."
    source venv/bin/activate
fi

echo "📰 Generating today's news report..."
# python main.py
echo "🦠 Skipping news generation..."

echo "🌐 Building HTML documentation..."
python generate_html/generate_html.py

# echo "🔍 Opening generated HTML page..."
# cd ..
# open index.html

cd ..
echo "🔄 Pushing to github..."
git add .
git commit -m "Daily deployment $(date +%Y:%m:%d-%H:%M:%S)"
git push

echo "🔗 Open site in browser..."
# open https://fastaiconsulting-net.github.io/younews/
open index.html


# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "👋 Deactivating virtual environment..."
    deactivate
fi

echo "✨ Daily deployment completed successfully!"
