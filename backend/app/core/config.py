from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGO_DB_NAME", "vitiscan_v3")

# JWT Configuration - CRITICAL: Must be set in .env file
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable must be set")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
if not REFRESH_SECRET_KEY:
    raise ValueError("REFRESH_SECRET_KEY environment variable must be set")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password Security
PASSWORD_PEPPER = os.getenv("PASSWORD_PEPPER", "")

# CORS Configuration - CRITICAL: Must be restrictive in production
ENV = os.getenv("ENV", "development")
if ENV == "production":
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
    if not ALLOWED_ORIGINS:
        raise ValueError("ALLOWED_ORIGINS must be set in production")
    CORS_ORIGINS = ALLOWED_ORIGINS.split(",")
else:
    CORS_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_V3 = os.getenv("AWS_REGION_V3", "eu-west-3")
AWS_REGION_AI_V3 = os.getenv("AWS_REGION_AI_V3", "eu-north-1")
S3_BUCKET_V3 = os.getenv("S3_BUCKET_V3", "vitiscanpro-v3-eu-west-3")
S3_BUCKET_V3_STAGING = os.getenv("S3_BUCKET_V3_STAGING", "vitiscanpro-v3-staging-eu-west-3")
S3_BUCKET_AI_IMAGES_V3 = os.getenv("S3_BUCKET_AI_IMAGES_V3", "vitiscan-ai-images-v3-eu-north-1")

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID")

# Email Configuration (Resend)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vitiscan.com")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@vitiscan.com")

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Weather & Satellite API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SENTINEL_HUB_API_KEY = os.getenv("SENTINEL_HUB_API_KEY")
SENTINEL_HUB_SERVICE_ID = os.getenv("SENTINEL_HUB_SERVICE_ID")

# E-Phy (Anses) Dataset Sync
EPHY_DATASET_API_URL = os.getenv(
    "EPHY_DATASET_API_URL",
    "https://www.data.gouv.fr/api/1/datasets/"
    "donnees-ouvertes-du-catalogue-e-phy-des-produits-phytopharmaceutiques-"
    "matieres-fertilisantes-et-supports-de-culture-adjuvants-produits-mixtes-et-melanges/",
)
EPHY_STORAGE_PATH = os.getenv("EPHY_STORAGE_PATH", "data/ephy/ephy.sqlite")

# Registration token secret (Base64 or raw). If not set, a dev key is derived from JWT_SECRET_KEY
REGISTRATION_SECRET_KEY = os.getenv("REGISTRATION_SECRET_KEY")

EPHY_VITICULTURE_ONLY = os.getenv("EPHY_VITICULTURE_ONLY", "true").lower() == "true"

# File Upload Configuration - V5.1 Fix
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/")
ALLOWED_FILE_EXTENSIONS = os.getenv("ALLOWED_FILE_EXTENSIONS", ".jpg,.jpeg,.png,.tiff,.geotiff,.pdf").split(",")
ALLOWED_MIME_TYPES = os.getenv("ALLOWED_MIME_TYPES", "image/jpeg,image/png,image/tiff,application/pdf").split(",")

# Virus Scanning
VIRUS_SCAN_ENABLED = os.getenv("VIRUS_SCAN_ENABLED", "false").lower() == "true"
CLAMAV_HOST = os.getenv("CLAMAV_HOST", "localhost")
CLAMAV_PORT = int(os.getenv("CLAMAV_PORT", "3310"))

# Treatments Configuration
TREATMENT_PRODUCTS = os.getenv(
    "TREATMENT_PRODUCTS",
    "Mancozeb,Cupru,Zeama bordeleză,Sulf,Azoxistrobin,Trichoderma,Glyphosate,Spinosad,Abamectin,Bacillus thuringiensis"
).split(",")
TREATMENT_PRODUCTS = [p.strip() for p in TREATMENT_PRODUCTS if p.strip()]
ALLOW_CUSTOM_TREATMENT_PRODUCTS = os.getenv("ALLOW_CUSTOM_TREATMENT_PRODUCTS", "true").lower() == "true"

# HTTPS Enforcement - V3.1 Fix
FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"
HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))
