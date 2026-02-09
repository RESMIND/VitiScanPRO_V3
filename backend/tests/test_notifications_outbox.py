import pytest
from app.core import notifications
from app.core import database as database_module

# Skip these tests when MongoDB is not reachable in local dev environments
if getattr(database_module, "db", None) is None:
    pytest.skip("MongoDB not available - skipping outbox tests", allow_module_level=True)

@pytest.mark.asyncio
async def test_email_outbox_saved():
    # Ensure outbox is empty
    await database_module.db["email_outbox"].delete_many({})
    # Send beta approved email - will be saved to outbox if RESEND_API_KEY not set
    await notifications.email_notifier.send_beta_approved_email("user@example.com", "Test Name", "tokentest", "http://localhost")
    count = await database_module.db["email_outbox"].count_documents({"to_email": "user@example.com"})
    assert count >= 1

@pytest.mark.asyncio
async def test_sms_outbox_saved():
    # Ensure outbox is empty
    await database_module.db["sms_outbox"].delete_many({})
    sent = notifications.sms_notifier.send_verification_code("+40700123456", "123456")
    # send_verification_code returns True when saved to outbox
    assert sent is True
    count = await database_module.db["sms_outbox"].count_documents({"to_phone": "+40700123456"})
    assert count >= 1
