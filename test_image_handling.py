#!/usr/bin/env python3
"""
Test script for WhatsApp image handling functionality
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from coach_core.user_memory import user_memory_db

def test_image_handling():
    """Test the image handling functionality"""
    print("🧪 Testing WhatsApp Image Handling")
    print("=" * 50)
    
    # Test user ID
    test_user_id = "1234567890"
    
    # Simulate a training image log
    training_log = {
        "type": "training_image",
        "image_path": "training_images/1234567890/training_20241201_143022.jpg",
        "caption": "Today's mobility session - feeling great!",
        "timestamp": datetime.now().isoformat(),
        "mime_type": "image/jpeg"
    }
    
    print(f"📸 Storing training image for user {test_user_id}")
    print(f"📝 Caption: {training_log['caption']}")
    print(f"📁 Path: {training_log['image_path']}")
    
    # Store the training image
    success = user_memory_db.store_training_image(test_user_id, training_log)
    
    if success:
        print("✅ Training image stored successfully")
        
        # Retrieve training images
        images = user_memory_db.get_user_training_images(test_user_id, limit=5)
        print(f"📊 Retrieved {len(images)} training images")
        
        for i, image in enumerate(images, 1):
            print(f"  {i}. {image['caption']} ({image['timestamp']})")
    else:
        print("❌ Failed to store training image")
    
    print("\n" + "=" * 50)
    print("✅ Image handling test completed")

if __name__ == "__main__":
    test_image_handling() 