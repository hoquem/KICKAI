#!/usr/bin/env python3
"""
Test script to verify Telegram markdown formatting.
"""

def test_markdown_formatting():
    """Test various markdown formatting examples."""
    
    # Test cases
    test_cases = [
        {
            "name": "Simple bold text",
            "text": "**Hello World**",
            "expected": "**Hello World**"
        },
        {
            "name": "Bold with exclamation",
            "text": "**Match Created Successfully!**",
            "expected": "**Match Created Successfully\\!**"
        },
        {
            "name": "Code block",
            "text": "`match_id_123`",
            "expected": "`match_id_123`"
        },
        {
            "name": "Mixed formatting",
            "text": "✅ **Match Created Successfully!**\n\n🏆 **League**\n⚽ **BP Hatters FC vs Arsenal**",
            "expected": "✅ **Match Created Successfully\\!**\n\n🏆 **League**\n⚽ **BP Hatters FC vs Arsenal**"
        }
    ]
    
    print("🧪 Testing Telegram MarkdownV2 Formatting")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['text']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Check if input needs escaping
        needs_escaping = test_case['text'] != test_case['expected']
        if needs_escaping:
            print("   ⚠️  Needs escaping for MarkdownV2")
        else:
            print("   ✅ No escaping needed")
    
    print("\n" + "=" * 50)
    print("💡 Key points for Telegram MarkdownV2:")
    print("• Escape these characters: . ! ( ) [ ] { } < > # + - = |")
    print("• Use ** for bold text")
    print("• Use ` for inline code")
    print("• Use \\n for line breaks")

if __name__ == "__main__":
    test_markdown_formatting() 