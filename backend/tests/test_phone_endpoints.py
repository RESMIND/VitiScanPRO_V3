#!/usr/bin/env python3
"""Integration tests for phone endpoints"""
import pytest

@pytest.mark.asyncio
async def test_send_verification_formats(client):
    valid_inputs = ["06 12 34 56 78", "0033 6 12 34 56 78", "+33 6 12 34 56 78", "0612345678"]
    for phone in valid_inputs:
        resp = await client.post("/send-verification-code", json={"phone": phone})
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_send_verification_invalid(client):
    invalids = ["+441234567890", "12345", "+331234567890"]
    for phone in invalids:
        resp = await client.post("/send-verification-code", json={"phone": phone})
        assert resp.status_code == 400