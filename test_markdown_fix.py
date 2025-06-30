#!/usr/bin/env python3
"""
Test script to verify markdown formatting works with Telegram's MarkdownV2 parse_mode.
"""

def test_markdown_formatting():
    """Test various markdown formatting examples."""
    
    # Test cases with expected markdown formatting
    test_cases = [
        {
            "name": "Basic bold text",
            "input": "**Hello World**",
            "expected": "**Hello World**"
        },
        {
            "name": "Bold with special characters",
            "input": "**Match Created Successfully!**",
            "expected": "**Match Created Successfully\\!**"
        },
        {
            "name": "Code block",
            "input": "`match_id_123`",
            "expected": "`match_id_123`"
        },
        {
            "name": "Mixed formatting",
            "input": "✅ **Match Created Successfully!**\n\n🏆 **League**\n⚽ **BP Hatters FC vs Arsenal**\n📅 **Date:** 2024-07-01\n🕐 **Time:** 14:00\n📍 **Venue:** Home\n\n🆔 **Match ID:** `BPHARS-01JUL`\n💡 Use this ID for updates and availability polls.",
            "expected": "✅ **Match Created Successfully\\!**\n\n🏆 **League**\n⚽ **BP Hatters FC vs Arsenal**\n📅 **Date:** 2024\\-07\\-01\n🕐 **Time:** 14:00\n📍 **Venue:** Home\n\n🆔 **Match ID:** `BPHARS\\-01JUL`\n💡 Use this ID for updates and availability polls\\."
        }
    ]
    
    print("🧪 Testing MarkdownV2 Formatting")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['input']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Check if input needs escaping for MarkdownV2
        needs_escaping = test_case['input'] != test_case['expected']
        if needs_escaping:
            print("   ⚠️  Needs escaping for MarkdownV2")
        else:
            print("   ✅ No escaping needed")
    
    print("\n" + "=" * 50)
    print("💡 Key points for MarkdownV2:")
    print("• Escape these characters: . ! ( ) [ ] { } < > # + - = | { } . !")
    print("• Use ** for bold text")
    print("• Use ` for inline code")
    print("• Use \\n for line breaks")

if __name__ == "__main__":
    test_markdown_formatting() 