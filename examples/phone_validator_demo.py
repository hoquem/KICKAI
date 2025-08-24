#!/usr/bin/env python3
"""
Demonstration of PhoneValidator using Google phonenumbers library.

This script shows the capabilities of the updated PhoneValidator class
for phone number validation, normalization, and formatting.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kickai.agents.utils.phone_validator import PhoneValidator


def demo_phone_validation():
    """Demonstrate phone number validation capabilities."""
    print("🔍 PhoneValidator Demo - Using Google phonenumbers Library")
    print("=" * 60)
    
    # Test phone numbers
    test_numbers = [
        "+1-202-555-0123",      # US number
        "(202) 555-0123",        # US number with parentheses
        "202-555-0123",          # US number with dashes
        "2025550123",            # US number without formatting
        "+44 20 7946 0958",      # UK number
        "+33 1 42 86 30 00",     # French number
        "+49 30 12345678",       # German number
        "invalid-number",        # Invalid number
        "123",                   # Too short
        "",                      # Empty string
    ]
    
    print("\n📱 Phone Number Validation:")
    print("-" * 30)
    
    for number in test_numbers:
        is_valid = PhoneValidator.looks_like_phone_number(number)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"{number:20} -> {status}")
    
    print("\n🔄 Phone Number Normalization:")
    print("-" * 30)
    
    for number in test_numbers:
        normalized = PhoneValidator.normalize_phone_number(number)
        if normalized:
            print(f"{number:20} -> {normalized}")
        else:
            print(f"{number:20} -> Cannot normalize")
    
    print("\n🔗 Phone Number Validation for Linking:")
    print("-" * 40)
    
    for number in test_numbers:
        is_valid, result = PhoneValidator.validate_phone_for_linking(number)
        if is_valid:
            print(f"{number:20} -> ✅ Valid: {result}")
        else:
            print(f"{number:20} -> ❌ Invalid: {result}")
    
    print("\n📊 Detailed Phone Information:")
    print("-" * 30)
    
    # Show detailed info for a valid number
    valid_number = "+1-202-555-0123"
    phone_info = PhoneValidator.get_phone_info(valid_number)
    
    if phone_info:
        print(f"Phone: {valid_number}")
        print(f"  Valid: {phone_info['is_valid']}")
        print(f"  Possible: {phone_info['is_possible']}")
        print(f"  Country Code: {phone_info['country_code']}")
        print(f"  Number Type: {phone_info['number_type']}")
        print(f"  E.164 Format: {phone_info['e164_format']}")
        print(f"  National Format: {phone_info['national_format']}")
        print(f"  International Format: {phone_info['international_format']}")
        print(f"  Country Calling Code: +{phone_info['country_calling_code']}")
    
    print("\n📱 Mobile Number Detection:")
    print("-" * 30)
    
    mobile_test_numbers = [
        "+1-202-555-0123",  # US number (may or may not be mobile)
        "+44 20 7946 0958",  # UK number
    ]
    
    for number in mobile_test_numbers:
        is_mobile = PhoneValidator.is_mobile_number(number)
        status = "📱 Mobile" if is_mobile else "📞 Fixed"
        print(f"{number:20} -> {status}")
    
    print("\n🎨 Phone Number Formatting:")
    print("-" * 30)
    
    number_to_format = "+1-202-555-0123"
    formats = ["national", "international", "e164"]
    
    for format_type in formats:
        formatted = PhoneValidator.format_for_display(number_to_format, format_type)
        print(f"{format_type:15} -> {formatted}")
    
    print("\n🛡️ Security Features:")
    print("-" * 20)
    
    security_tests = [
        "1" * 1000,  # Extremely long input
        "202-555-0123<script>",  # XSS attempt
        "202-555-0123' OR 1=1--",  # SQL injection attempt
    ]
    
    for test_input in security_tests:
        is_valid = PhoneValidator.looks_like_phone_number(test_input)
        status = "✅ Allowed" if is_valid else "❌ Blocked"
        print(f"{test_input[:30]:30} -> {status}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("The PhoneValidator now uses Google's phonenumbers library for robust validation.")


if __name__ == "__main__":
    demo_phone_validation()
