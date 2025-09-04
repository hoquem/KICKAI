#!/usr/bin/env python3
"""
Script to switch back to Gemini configuration for immediate use.

This is useful when OpenAI quota is exceeded or GPT-4 access is denied.
"""

import os
import sys
from pathlib import Path

def switch_to_gemini():
    """Switch configuration to use Gemini."""
    
    print("🔄 Switching to Gemini Configuration...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current .env content
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        print("✅ .env file read successfully")
    except Exception as e:
        print(f"❌ Failed to read .env file: {e}")
        return False
    
    # Update configuration
    updated_content = content
    
    # Update AI provider
    if "AI_PROVIDER=openai" in content:
        updated_content = updated_content.replace("AI_PROVIDER=openai", "AI_PROVIDER=gemini")
        print("✅ Updated AI_PROVIDER to gemini")
    elif "AI_PROVIDER=gemini" in content:
        print("✅ AI_PROVIDER already set to gemini")
    else:
        print("⚠️ AI_PROVIDER not found, adding it")
        updated_content += "\nAI_PROVIDER=gemini\n"
    
    # Update model settings
    if "AI_MODEL_SIMPLE=gpt-3.5-turbo" in content:
        updated_content = updated_content.replace("AI_MODEL_SIMPLE=gpt-3.5-turbo", "AI_MODEL_SIMPLE=gemini-1.5-flash")
        print("✅ Updated AI_MODEL_SIMPLE to gemini-1.5-flash")
    elif "AI_MODEL_SIMPLE=gemini-1.5-flash" in content:
        print("✅ AI_MODEL_SIMPLE already set to gemini-1.5-flash")
    else:
        print("⚠️ AI_MODEL_SIMPLE not found, adding it")
        updated_content += "\nAI_MODEL_SIMPLE=gemini-1.5-flash\n"
    
    if "AI_MODEL_ADVANCED=gpt-4" in content:
        updated_content = updated_content.replace("AI_MODEL_ADVANCED=gpt-4", "AI_MODEL_ADVANCED=gemini-1.5-pro")
        print("✅ Updated AI_MODEL_ADVANCED to gemini-1.5-pro")
    elif "AI_MODEL_ADVANCED=gemini-1.5-pro" in content:
        print("✅ AI_MODEL_ADVANCED already set to gemini-1.5-pro")
    else:
        print("⚠️ AI_MODEL_ADVANCED not found, adding it")
        updated_content += "\nAI_MODEL_ADVANCED=gemini-1.5-pro\n"
    
    # Write updated content
    try:
        with open(env_file, 'w') as f:
            f.write(updated_content)
        print("✅ .env file updated successfully")
    except Exception as e:
        print(f"❌ Failed to write .env file: {e}")
        return False
    
    print("\n🎉 Configuration switched to Gemini!")
    print("📋 Updated settings:")
    print("- AI_PROVIDER=gemini")
    print("- AI_MODEL_SIMPLE=gemini-1.5-flash")
    print("- AI_MODEL_ADVANCED=gemini-1.5-pro")
    
    print("\n📋 Next steps:")
    print("1. Ensure GOOGLE_API_KEY is set in your .env file")
    print("2. Restart your application")
    print("3. The system will now use Gemini models")
    
    return True

def main():
    """Main function."""
    print("🚀 Gemini Configuration Switch")
    print("=" * 50)
    
    success = switch_to_gemini()
    
    if success:
        print("\n✅ Successfully switched to Gemini configuration!")
        print("🔄 Please restart your application to apply changes.")
    else:
        print("\n❌ Failed to switch configuration.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
