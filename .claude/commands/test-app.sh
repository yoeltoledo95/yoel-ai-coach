#!/bin/bash
# Test the current AI coach app

echo "🧪 Testing AI Coach App..."

# Check if app is running
if curl -s http://localhost:8001/api/health > /dev/null; then
    echo "✅ App is running on port 8001"
else
    echo "❌ App is not running. Starting it..."
    python src/main.py &
    sleep 3
fi

# Test basic chat functionality
echo "📝 Testing chat functionality..."
response=$(curl -s -X POST http://localhost:8001/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello, I want to work on my handstand today"}')

if [ $? -eq 0 ]; then
    echo "✅ Chat test successful"
    echo "Response: $response" | head -c 200
    echo "..."
else
    echo "❌ Chat test failed"
fi

echo "🎯 Test complete!"
