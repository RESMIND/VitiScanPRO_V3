"""
VitiScan v3 - Comprehensive System Audit
Checks security, functionality, configuration, and code quality
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

class Auditor:
    def __init__(self):
        self.score = 0
        self.max_score = 0
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def check(self, name: str, condition: bool, points: int, issue_msg: str = ""):
        """Check a condition and update score"""
        self.max_score += points
        if condition:
            self.score += points
            self.successes.append(f"✓ {name}")
            return True
        else:
            self.issues.append(f"✗ {name}: {issue_msg}")
            return False
    
    def warn(self, message: str):
        """Add a warning"""
        self.warnings.append(f"⚠ {message}")
    
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
        print(f"{BLUE}{BOLD}  {title}{RESET}")
        print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")


async def audit_security():
    """Audit security configuration"""
    print(f"{CYAN}[1/8] Security Configuration{RESET}")
    auditor = Auditor()
    
    # JWT Configuration
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    auditor.check(
        "JWT Secret Key configured",
        jwt_secret and len(jwt_secret) >= 32,
        10,
        "JWT secret too short or missing"
    )
    
    # Check if using default/weak keys
    weak_keys = ["secret", "password", "123456", "admin"]
    is_strong = jwt_secret and not any(weak in jwt_secret.lower() for weak in weak_keys)
    auditor.check(
        "JWT Secret Key is strong",
        is_strong,
        10,
        "JWT secret appears weak"
    )
    
    # CORS Configuration
    cors_origins = os.getenv("CORS_ORIGINS", "")
    auditor.check(
        "CORS origins configured",
        bool(cors_origins),
        5,
        "CORS not configured"
    )
    
    # Check if CORS is not wildcard in production
    is_secure_cors = "*" not in cors_origins
    auditor.check(
        "CORS not using wildcard (*)",
        is_secure_cors,
        5,
        "Wildcard CORS is insecure"
    )
    
    # Password hashing check (check if bcrypt is installed)
    try:
        import bcrypt
        auditor.check("Password hashing library (bcrypt) installed", True, 10, "")
    except ImportError:
        auditor.check("Password hashing library (bcrypt) installed", False, 10, "bcrypt not installed")
    
    # Rate limiting check
    try:
        import slowapi
        auditor.check("Rate limiting library (slowapi) installed", True, 10, "")
    except ImportError:
        auditor.check("Rate limiting library (slowapi) installed", False, 10, "slowapi not installed")
    
    return auditor


async def audit_database():
    """Audit database connection and setup"""
    print(f"{CYAN}[2/8] Database Configuration{RESET}")
    auditor = Auditor()
    
    mongodb_url = os.getenv("MONGODB_URL")
    auditor.check(
        "MongoDB URL configured",
        bool(mongodb_url),
        10,
        "MongoDB URL not set"
    )
    
    # Test connection
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(mongodb_url)
        await client.admin.command('ping')
        auditor.check("MongoDB connection successful", True, 15, "")
        
        # Check database name
        db_name = os.getenv("MONGODB_DB_NAME")
        auditor.check("Database name configured", bool(db_name), 5, "")
        
        client.close()
    except Exception as e:
        auditor.check("MongoDB connection successful", False, 15, str(e)[:50])
    
    return auditor


async def audit_storage():
    """Audit file storage configuration"""
    print(f"{CYAN}[3/8] File Storage (AWS S3){RESET}")
    auditor = Auditor()
    
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    auditor.check("AWS Access Key configured", bool(aws_key), 5, "")
    auditor.check("AWS Secret Key configured", bool(aws_secret), 5, "")
    
    # Test S3 access
    if aws_key and aws_secret:
        try:
            import boto3
            s3 = boto3.client(
                's3',
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
                region_name=os.getenv("AWS_REGION_V3")
            )
            bucket = os.getenv("S3_BUCKET_V3")
            s3.head_bucket(Bucket=bucket)
            auditor.check("S3 bucket accessible", True, 10, "")
            
            # Check multiple buckets
            bucket_ai = os.getenv("S3_BUCKET_AI_IMAGES_V3")
            if bucket_ai:
                auditor.check("AI images bucket configured", True, 5, "")
        except Exception as e:
            auditor.check("S3 bucket accessible", False, 10, str(e)[:50])
    
    return auditor


async def audit_notifications():
    """Audit notification services"""
    print(f"{CYAN}[4/8] Notification Services{RESET}")
    auditor = Auditor()
    
    # Telegram
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
    
    if telegram_token and telegram_chat:
        try:
            from telegram import Bot
            bot = Bot(token=telegram_token)
            await bot.get_me()
            auditor.check("Telegram Bot configured and working", True, 10, "")
        except Exception as e:
            auditor.check("Telegram Bot configured and working", False, 10, str(e)[:50])
    else:
        auditor.warn("Telegram Bot not configured (optional)")
    
    # Email (Resend)
    resend_key = os.getenv("RESEND_API_KEY")
    if resend_key and resend_key != "your_resend_api_key_here":
        auditor.check("Email service (Resend) configured", True, 10, "")
    else:
        auditor.warn("Email service not configured (required for beta)")
    
    # SMS (Twilio)
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if twilio_sid and twilio_token:
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            account = client.api.accounts(twilio_sid).fetch()
            auditor.check("SMS service (Twilio) configured and working", True, 10, "")
        except Exception as e:
            auditor.check("SMS service (Twilio) configured and working", False, 10, str(e)[:50])
    else:
        auditor.warn("SMS service not configured (required for phone verification)")
    
    return auditor


async def audit_api_endpoints():
    """Audit API endpoints structure"""
    print(f"{CYAN}[5/8] API Endpoints{RESET}")
    auditor = Auditor()
    
    # Check if main.py exists
    main_file = Path("app/main.py")
    auditor.check("main.py exists", main_file.exists(), 5, "Main app file missing")
    
    # Check route files
    routes_dir = Path("app/routes")
    if routes_dir.exists():
        route_files = list(routes_dir.glob("*.py"))
        auditor.check(
            f"Route files present ({len(route_files)} found)",
            len(route_files) >= 5,
            10,
            f"Expected at least 5 route files, found {len(route_files)}"
        )
        
        expected_routes = ["auth.py", "users.py", "establishments.py", "parcels.py", "crops.py"]
        for route in expected_routes:
            route_path = routes_dir / route
            if route_path.exists():
                auditor.check(f"Route {route} exists", True, 2, "")
    else:
        auditor.check("Routes directory exists", False, 10, "app/routes not found")
    
    return auditor


async def audit_code_quality():
    """Audit code quality and best practices"""
    print(f"{CYAN}[6/8] Code Quality{RESET}")
    auditor = Auditor()
    
    # Check for environment file
    env_file = Path(".env")
    auditor.check(".env file exists", env_file.exists(), 5, "")
    
    # Check for requirements.txt
    req_file = Path("requirements.txt")
    auditor.check("requirements.txt exists", req_file.exists(), 5, "")
    
    # Check for .gitignore
    gitignore = Path(".gitignore")
    if gitignore.exists():
        content = gitignore.read_text()
        auditor.check(".gitignore includes .env", ".env" in content, 5, "Secrets may be committed")
        auditor.check(".gitignore includes __pycache__", "__pycache__" in content, 2, "")
    else:
        auditor.warn(".gitignore not found")
    
    # Check core modules
    core_dir = Path("app/core")
    if core_dir.exists():
        core_files = ["config.py", "security.py", "database.py"]
        for core_file in core_files:
            path = core_dir / core_file
            auditor.check(f"Core module {core_file} exists", path.exists(), 3, "")
    
    return auditor


async def audit_dependencies():
    """Audit installed dependencies"""
    print(f"{CYAN}[7/8] Dependencies{RESET}")
    auditor = Auditor()
    
    required_packages = [
        ("fastapi", "Web framework"),
        ("uvicorn", "ASGI server"),
        ("motor", "MongoDB async driver"),
        ("jose", "JWT tokens"),
        ("bcrypt", "Password hashing"),
        ("boto3", "AWS S3 client"),
        ("slowapi", "Rate limiting"),
        ("resend", "Email service"),
        ("telegram", "Telegram notifications"),
        ("twilio.rest", "SMS service")
    ]
    
    for package, description in required_packages:
        try:
            __import__(package.replace("-", "_"))
            auditor.check(f"{package} - {description}", True, 2, "")
        except ImportError:
            auditor.check(f"{package} - {description}", False, 2, f"{package} not installed")
    
    return auditor


async def audit_external_apis():
    """Audit external API integrations"""
    print(f"{CYAN}[8/8] External API Integrations{RESET}")
    auditor = Auditor()
    
    # OpenWeather
    openweather_key = os.getenv("OPENWEATHER_API_KEY")
    if openweather_key and openweather_key != "your_openweather_api_key_here":
        try:
            import requests
            r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q=Paris&appid={openweather_key}", timeout=5)
            if r.status_code == 200:
                auditor.check("OpenWeather API working", True, 5, "")
            else:
                auditor.warn("OpenWeather API key configured but not working (may need activation time)")
        except Exception as e:
            auditor.warn(f"OpenWeather API test failed: {str(e)[:50]}")
    else:
        auditor.warn("OpenWeather API not configured (optional)")
    
    # Sentinel Hub
    sentinel_key = os.getenv("SENTINEL_HUB_API_KEY")
    if sentinel_key and sentinel_key not in ["your_sentinel_hub_api_key_here", "grape-guard"]:
        auditor.check("Sentinel Hub API configured", True, 5, "")
    else:
        auditor.warn("Sentinel Hub API not configured (optional)")
    
    return auditor


async def main():
    """Run complete audit"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{'  VitiScan v3 - Comprehensive System Audit':^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    auditors = []
    
    # Run all audits
    auditors.append(await audit_security())
    auditors.append(await audit_database())
    auditors.append(await audit_storage())
    auditors.append(await audit_notifications())
    auditors.append(await audit_api_endpoints())
    auditors.append(await audit_code_quality())
    auditors.append(await audit_dependencies())
    auditors.append(await audit_external_apis())
    
    # Calculate totals
    total_score = sum(a.score for a in auditors)
    max_score = sum(a.max_score for a in auditors)
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Print summary
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}  AUDIT SUMMARY{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    # Overall score
    if percentage >= 90:
        color = GREEN
        grade = "EXCELLENT"
    elif percentage >= 80:
        color = GREEN
        grade = "GOOD"
    elif percentage >= 70:
        color = YELLOW
        grade = "FAIR"
    else:
        color = RED
        grade = "NEEDS IMPROVEMENT"
    
    print(f"{BOLD}Overall Score: {color}{total_score}/{max_score} ({percentage:.1f}%) - {grade}{RESET}\n")
    
    # Issues
    all_issues = []
    for auditor in auditors:
        all_issues.extend(auditor.issues)
    
    if all_issues:
        print(f"{RED}{BOLD}Critical Issues ({len(all_issues)}):{RESET}")
        for issue in all_issues[:10]:  # Show top 10
            print(f"  {RED}{issue}{RESET}")
        if len(all_issues) > 10:
            print(f"  {YELLOW}...and {len(all_issues) - 10} more issues{RESET}")
        print()
    
    # Warnings
    all_warnings = []
    for auditor in auditors:
        all_warnings.extend(auditor.warnings)
    
    if all_warnings:
        print(f"{YELLOW}{BOLD}Warnings ({len(all_warnings)}):{RESET}")
        for warning in all_warnings[:5]:  # Show top 5
            print(f"  {YELLOW}{warning}{RESET}")
        if len(all_warnings) > 5:
            print(f"  {YELLOW}...and {len(all_warnings) - 5} more warnings{RESET}")
        print()
    
    # Recommendations
    print(f"{CYAN}{BOLD}Recommendations:{RESET}")
    
    if percentage < 80:
        print(f"  • {YELLOW}Address critical security issues immediately{RESET}")
    
    if any("Email" in w for w in all_warnings):
        print(f"  • {YELLOW}Configure email service for beta onboarding{RESET}")
    
    if any("SMS" in w for w in all_warnings):
        print(f"  • {YELLOW}Configure SMS service for phone verification{RESET}")
    
    if any("OpenWeather" in w for w in all_warnings):
        print(f"  • Wait 15-30 minutes for OpenWeather API key activation")
    
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}  Audit Complete{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    return percentage >= 70


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Audit interrupted{RESET}")
        sys.exit(1)
