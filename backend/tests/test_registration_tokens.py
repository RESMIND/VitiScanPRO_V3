import pytest
import time
from app.core import registration_tokens as rt

@pytest.mark.asyncio
async def test_generate_validate_token():
    token = rt.generate_registration_token("12345", "test@example.com", ttl_seconds=60)
    assert token is not None

    validated = rt.validate_registration_token(token)
    assert validated["payload"]["beta_request_id"] == "12345"
    assert validated["payload"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_expired_token():
    token = rt.generate_registration_token("1", "a@b.com", ttl_seconds=1)
    time.sleep(2)
    with pytest.raises(ValueError):
        rt.validate_registration_token(token)

def test_tampered_token():
    token = rt.generate_registration_token("9", "x@y.com", ttl_seconds=60)
    parts = token.split('.')
    assert len(parts) == 3
    # tamper with payload
    parts[1] = parts[1][::-1]
    tampered = '.'.join(parts)
    with pytest.raises(ValueError):
        rt.validate_registration_token(tampered)
