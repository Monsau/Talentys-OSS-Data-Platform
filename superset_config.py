# Apache Superset Configuration for Phase 3 Dashboard

# Secret key for session management (CHANGE IN PRODUCTION!)
SECRET_KEY = 'superset_secret_key_change_me_in_production'

# Database connection (managed by Docker Compose)
# No need to set SQLALCHEMY_DATABASE_URI - handled by environment variables

# Enable CORS for API access
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']
}

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_FILTERS_EXPERIMENTAL': True,
    'ENABLE_EXPLORE_DRAG_AND_DROP': True,
}

# Dashboard settings
DASHBOARD_AUTO_REFRESH_MODE = "change"
DASHBOARD_AUTO_REFRESH_INTERVALS = [
    [5, "5 seconds"],
    [10, "10 seconds"],
    [30, "30 seconds"],
    [60, "1 minute"],
    [300, "5 minutes"],
]

# Chart settings
PREVENT_UNSAFE_DB_CONNECTIONS = False  # Allow Dremio connection
SQLLAB_ASYNC_TIME_LIMIT_SEC = 300

# Cache configuration (Redis)
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'superset-redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
}

# Data cache
DATA_CACHE_CONFIG = CACHE_CONFIG

# Allow CSV/Excel export
CSV_EXPORT = {
    "encoding": "utf-8",
}

# SQL Lab settings
SQLLAB_TIMEOUT = 300
SQLLAB_DEFAULT_DBID = None

# Logging
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = logging.INFO
FILENAME = '/app/superset_home/superset.log'
ROLLOVER = 'midnight'
INTERVAL = 1
BACKUP_COUNT = 30

# Email configuration (optional)
# SMTP_HOST = 'smtp.gmail.com'
# SMTP_STARTTLS = True
# SMTP_SSL = False
# SMTP_USER = 'your_email@gmail.com'
# SMTP_PORT = 587
# SMTP_PASSWORD = 'your_password'
# SMTP_MAIL_FROM = 'your_email@gmail.com'

# Webdriver for screenshot generation (optional)
# WEBDRIVER_TYPE = "chrome"
# WEBDRIVER_OPTION_ARGS = [
#     "--headless",
#     "--no-sandbox",
#     "--disable-dev-shm-usage",
# ]

print("✅ Superset configuration loaded for Phase 3 Dashboard")
