#!/usr/bin/env python3
"""
Test script to verify markdown escaping for Telegram MarkdownV2.
"""

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram's MarkdownV2 parse_mode."""
    # Characters that need to be escaped in MarkdownV2
    special_chars = ['.', '!', '(', ')', '[', ']', '{', '}', '<', '>', '#', '+', '-', '=', '|', ':', '~', '`']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def test_markdown_escaping():
    """Test various markdown formatting examples."""
    
    test_cases = [
        {
            "name": "Simple bold text",
            "input": "**Hello World**",
            "expected": "**Hello World**"
        },
        {
            "name": "Bold with colon",
            "input": "**Player Management:**",
            "expected": "**Player Management\\:**"
        },
        {
            "name": "Bold with exclamation",
            "input": "**Match Created Successfully!**",
            "expected": "**Match Created Successfully\\!**"
        },
        {
            "name": "Code block",
            "input": "`match_id_123`",
            "expected": "`match_id_123`"
        },
        {
            "name": "Mixed formatting with special chars",
            "input": "✅ **Match Created Successfully!**\n\n🏆 **League**\n⚽ **BP Hatters FC vs Arsenal**\n📅 **Date:** 2024-07-01",
            "expected": "✅ **Match Created Successfully\\!**\n\n🏆 **League**\n⚽ **BP Hatters FC vs Arsenal**\n📅 **Date\\:** 2024\\-07\\-01"
        },
        {
            "name": "Help message example",
            "input": "🤖 **KICKAI Bot Help (Admin)**\n\n**Available Commands:**\n\n**Player Management:**\n• \"Add player John Doe with phone 123456789\"",
            "expected": "🤖 **KICKAI Bot Help \\(Admin\\)**\n\n**Available Commands:**\n\n**Player Management\\:**\n• \"Add player John Doe with phone 123456789\""
        }
    ]
    
    print("🧪 Testing MarkdownV2 Escaping")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['input']}")
        
        escaped = escape_markdown_v2(test_case['input'])
        print(f"   Escaped: {escaped}")
        
        # Check if it matches expected
        if escaped == test_case['expected']:
            print("   ✅ Matches expected")
        else:
            print(f"   ❌ Expected: {test_case['expected']}")
            print("   ⚠️  Does not match expected")
    
    print("\n" + "=" * 50)
    print("💡 Key points for Telegram MarkdownV2:")
    print("• Escape these characters: . ! ( ) [ ] { } < > # + - = | : ~ `")
    print("• Use ** for bold text")
    print("• Use ` for inline code")
    print("• Use \\n for line breaks")

if __name__ == "__main__":
    test_markdown_escaping() 