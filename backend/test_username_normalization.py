#!/usr/bin/env python3
"""Tests for username normalization and validation"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.utils import normalize_username, is_valid_username, is_reserved_username


def test_normalize_username_basic():
    assert normalize_username("Jean Pierre") == "jean-pierre"
    assert normalize_username("Jean_Pierre") == "jean-pierre"
    assert normalize_username("Jean!Pierre") == "jeanpierre"
    assert normalize_username("  Jean--Pierre__ ") == "jean-pierre"


def test_is_valid_username():
    assert is_valid_username("jean-pierre")
    assert not is_valid_username("ab")  # too short
    assert not is_valid_username("a" * 31)  # too long
    assert not is_valid_username("invalid@name")


def test_reserved_usernames():
    assert is_reserved_username("admin")
    assert not is_reserved_username("jean-pierre")


if __name__ == "__main__":
    test_normalize_username_basic()
    test_is_valid_username()
    test_reserved_usernames()
    print("✅ Username normalization tests passed")