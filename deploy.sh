#!/bin/bash

echo "🚀 Deploying Yoel's AI Coach..."

# Check if we're in the right directory
if [ ! -f "mobile_logger.py" ]; then
    echo "❌ Error: mobile_logger.py not found. Make sure you're in the project directory."
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Check if Heroku CLI is installed
if command -v heroku &> /dev/null; then
    echo "✅ Heroku CLI found"
    
    # Check if app already exists
    if heroku apps:info &> /dev/null; then
        echo "🔄 Updating existing Heroku app..."
        git add .
        git commit -m "Update AI coach"
        git push heroku main
    else
        echo "🆕 Creating new Heroku app..."
        heroku create yoel-ai-coach
        git push heroku main
    fi
    
    echo "🌐 Opening your app..."
    heroku open
    
elif command -v vercel &> /dev/null; then
    echo "✅ Vercel CLI found"
    echo "🚀 Deploying to Vercel..."
    vercel --prod
    
elif command -v railway &> /dev/null; then
    echo "✅ Railway CLI found"
    echo "🚀 Deploying to Railway..."
    railway up
    
else
    echo "❌ No deployment CLI found. Please install one of:"
    echo "   - Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
    echo "   - Vercel CLI: npm install -g vercel"
    echo "   - Railway CLI: npm install -g @railway/cli"
    echo ""
    echo "📋 Manual deployment options:"
    echo "1. Heroku (Recommended):"
    echo "   - Install Heroku CLI"
    echo "   - Run: heroku create yoel-ai-coach"
    echo "   - Run: git push heroku main"
    echo ""
    echo "2. Railway:"
    echo "   - Connect GitHub repo to Railway"
    echo "   - Auto-deploys from main branch"
    echo ""
    echo "3. Vercel:"
    echo "   - Install Vercel CLI"
    echo "   - Run: vercel --prod"
fi

echo "✅ Deployment complete!"
echo "📱 Your AI coach will be always accessible!" 