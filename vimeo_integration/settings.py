import os

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok.io', '.ngrok-free.app']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.ngrok.io',
    'https://*.ngrok-free.app',
]

# File upload settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Increase file upload size
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB
MAX_UPLOAD_SIZE = 524288000  # 500MB

# Increase timeout for large uploads
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

# Add CORS headers for ngrok
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.ngrok.io",
    "https://*.ngrok-free.app",
]

CORS_ALLOW_CREDENTIALS = True 