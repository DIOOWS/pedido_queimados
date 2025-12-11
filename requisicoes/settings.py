from pathlib import Path
import os
import dj_database_url

# ---------------------------------------------------------
# BASE DIR
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------
# SEGURANÇA
# ---------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

# ---------------------------------------------------------
# ALLOWED HOSTS
# ---------------------------------------------------------
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# Render preenche automaticamente
if "RENDER_EXTERNAL_HOSTNAME" in os.environ:
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])

# Se quiser deixar mais permissivo na fase de testes:
# ALLOWED_HOSTS.append("*")

# ---------------------------------------------------------
# APPS
# ---------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',  # seu app
]

# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # necessário no Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------------------------------------
# URLs / WSGI
# ---------------------------------------------------------
ROOT_URLCONF = 'requisicoes.urls'
WSGI_APPLICATION = 'requisicoes.wsgi.application'

# ---------------------------------------------------------
# DATABASE (Render → PostgreSQL | Local → SQLite)
# ---------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ---------------------------------------------------------
# INTERNACIONALIZAÇÃO
# ---------------------------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------
# ARQUIVOS ESTÁTICOS (WhiteNoise obrigatório)
# ---------------------------------------------------------
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "core" / "static",
    BASE_DIR / "staticfiles_root",
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------
# MEDIA
# ---------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------------------------------------
# AUTENTICAÇÃO
# ---------------------------------------------------------
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

# ---------------------------------------------------------
# PADRÕES
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
