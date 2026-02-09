#!/usr/bin/env python3
"""
Test script for phone verification system
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.routes.auth import generate_verification_code, store_verification_code, get_verification_code, normalize_phone, is_valid_phone

def test_phone_validation():
    """Test phone number validation"""
    print("🧪 Testing phone validation...")

    # Valid phones (France only)
    valid_phones = ["+33612345678", "0033612345678", "0612345678", "+33 6 12 34 56 78", "06 12 34 56 78"]
    for phone in valid_phones:
        normalized = normalize_phone(phone)
        is_valid = is_valid_phone(normalized)
        print(f"  {phone} -> {normalized} -> {'✅ Valid' if is_valid else '❌ Invalid'}")

    # Invalid phones
    invalid_phones = ["123456789", "+331234567890", "abc123", ""]
    for phone in invalid_phones:
        normalized = normalize_phone(phone)
        is_valid = is_valid_phone(normalized)
        print(f"  {phone} -> {normalized} -> {'✅ Valid' if is_valid else '❌ Invalid'}")

def test_verification_codes():
    """Test verification code generation and storage"""
    print("\n🧪 Testing verification codes...")

    # Test code generation
    codes = [generate_verification_code() for _ in range(5)]
    print(f"  Generated codes: {codes}")

    # Test code storage and retrieval
    phone = "+33612345678"
    code = "123456"

    store_verification_code(phone, code)
    retrieved = get_verification_code(phone)

    if retrieved and retrieved['code'] == code:
        print("  ✅ Code storage and retrieval works")
    else:
        print("  ❌ Code storage/retrieval failed")

    # Test non-existent phone
    fake_phone = "+33699999999"
    fake_retrieved = get_verification_code(fake_phone)
    if fake_retrieved is None:
        print("  ✅ Non-existent code returns None")
    else:
        print("  ❌ Non-existent code should return None")

if __name__ == "__main__":
    print("🚀 Testing Phone Verification System\n")

    test_phone_validation()
    test_verification_codes()

    print("\n✅ All tests completed!")