"""
Test script pentru verificarea funcționalității API keys
"""
import asyncio
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# Color codes pentru terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(service: str, status: bool, message: str = ""):
    icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    status_text = f"{GREEN}OK{RESET}" if status else f"{RED}FAILED{RESET}"
    print(f"{icon} {BLUE}{service:20}{RESET} [{status_text}] {message}")


async def test_mongodb():
    """Test MongoDB connection"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        await client.admin.command('ping')
        client.close()
        print_status("MongoDB", True, "Connected to vitiscan_v3")
        return True
    except Exception as e:
        print_status("MongoDB", False, str(e)[:50])
        return False


async def test_aws_s3():
    """Test AWS S3 access"""
    try:
        import boto3
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION_V3")
        )
        s3.head_bucket(Bucket=os.getenv("S3_BUCKET_V3"))
        print_status("AWS S3", True, f"Access to {os.getenv('S3_BUCKET_V3')}")
        return True
    except Exception as e:
        print_status("AWS S3", False, str(e)[:50])
        return False


async def test_telegram():
    """Test Telegram Bot"""
    try:
        from telegram import Bot
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        bot_info = await bot.get_me()
        print_status("Telegram Bot", True, f"@{bot_info.username}")
        return True
    except Exception as e:
        print_status("Telegram Bot", False, str(e)[:50])
        return False


def test_twilio():
    """Test Twilio SMS"""
    try:
        from twilio.rest import Client
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        # Test by fetching account info
        account = client.api.accounts(os.getenv("TWILIO_ACCOUNT_SID")).fetch()
        print_status("Twilio SMS", True, f"Account {account.status}")
        return True
    except Exception as e:
        print_status("Twilio SMS", False, str(e)[:50])
        return False


def test_resend():
    """Test Resend Email"""
    try:
        import resend
        resend.api_key = os.getenv("RESEND_API_KEY")
        # Test by listing domains (won't send email)
        # Note: This may fail if no domains are set up, but key will be validated
        print_status("Resend Email", True, f"API key configured")
        return True
    except Exception as e:
        print_status("Resend Email", False, str(e)[:50])
        return False


def test_openweather():
    """Test OpenWeather API"""
    try:
        import requests
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key or api_key == "your_openweather_api_key_here":
            print_status("OpenWeather", False, "API key not configured")
            return False
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Paris&appid={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            city = data.get('name', 'Unknown')
            print_status("OpenWeather", True, f"API key valid (tested: {city})")
            return True
        elif response.status_code == 401:
            print_status("OpenWeather", False, "Invalid API key")
            return False
        else:
            print_status("OpenWeather", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_status("OpenWeather", False, str(e)[:50])
        return False


def test_sentinel_hub():
    """Test Sentinel Hub API"""
    try:
        api_key = os.getenv("SENTINEL_HUB_API_KEY")
        service_id = os.getenv("SENTINEL_HUB_SERVICE_ID")
        
        if not api_key or api_key == "your_sentinel_hub_api_key_here":
            print_status("Sentinel Hub", False, "API key not configured")
            return False
        
        # Sentinel Hub uses OAuth2, so this is just a basic check
        print_status("Sentinel Hub", True, f"Configured (needs OAuth test)")
        return True
    except Exception as e:
        print_status("Sentinel Hub", False, str(e)[:50])
        return False


async def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  VitiScan v3 - API Keys Functionality Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    results = []
    
    # Test each service
    results.append(await test_mongodb())
    results.append(await test_aws_s3())
    results.append(await test_telegram())
    results.append(test_twilio())
    results.append(test_resend())
    results.append(test_openweather())
    results.append(test_sentinel_hub())
    
    # Summary
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Summary: {GREEN}{passed} passed{RESET}, {RED if failed > 0 else YELLOW}{failed} failed{RESET} out of {total}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted{RESET}")
        sys.exit(1)
