#!/usr/bin/env python3
"""
Script to fix HTML tags in telegram command handler by converting them to markdown format.
"""

import re

def fix_html_to_markdown(text):
    """Convert HTML tags to markdown format for Telegram MarkdownV2."""
    # Replace HTML tags with markdown
    text = re.sub(r'<b>(.*?)</b>', r'**\1**', text)
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text)
    
    # Escape special characters for MarkdownV2
    special_chars = ['.', '!', '(', ')', '[', ']', '{', '}', '<', '>', '#', '+', '-', '=', '|']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def test_fixes():
    """Test the HTML to markdown conversion."""
    test_cases = [
        "✅ <b>Match Created Successfully!</b>",
        "🏆 <b>League</b>",
        "🆔 <b>Match ID:</b> <code>BPHARS-01JUL</code>",
        "📊 <b>Bot Status</b>",
        "👤 <b>User:</b> John (@john_doe)",
        "❌ <b>Error:</b> Something went wrong",
        "💡 Type <code>/help</code> to see available commands."
    ]
    
    print("🧪 Testing HTML to Markdown conversion")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        fixed = fix_html_to_markdown(test_case)
        print(f"\n{i}. Original: {test_case}")
        print(f"   Fixed: {fixed}")

if __name__ == "__main__":
    test_fixes() 