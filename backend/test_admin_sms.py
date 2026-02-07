#!/usr/bin/env python3
"""
Test SMS sending to admin phone number
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.notifications import SMSNotifier

def test_admin_sms():
    """Send test SMS to admin phone number"""
    sms = SMSNotifier()

    if not sms.enabled:
        print("❌ SMS service is not configured")
        return False

    # Test with the second admin phone number (French format)
    admin_phone = "0033665017098"
    test_message = "VitiScan v3 - Confirmare număr înregistrat pentru admin. Acest mesaj confirmă că serviciul SMS funcționează."

    print(f"📱 Sending test SMS to {admin_phone}...")
    success = sms.send_sms(admin_phone, test_message)

    if success:
        print("✅ SMS sent successfully!")
        return True
    else:
        print("❌ Failed to send SMS")
        return False

if __name__ == "__main__":
    test_admin_sms()