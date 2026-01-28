from pathlib import Path
import os
import dj_database_url
from decouple import config

# ==============================================================================
# RUTAS BASE
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# SEGURIDAD
# ==============================================================================
# Lee la clave secreta del entorno (.env o Render)
SECRET_KEY = config('SECRET_KEY')

# En producción (Render) DEBUG debe ser False. En tu PC será True.
DEBUG = config('DEBUG', default=False, cast=bool)

# Permite cualquier host en Render (*), o los que definas.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')


# ==============================================================================
# APLICACIONES (APPS)
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # <--- CRUCIAL: Necesario para 'collectstatic'
    
    # Tus apps
    'core',
]


# ==============================================================================
# MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- CRUCIAL: Para servir archivos en Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# ==============================================================================
# BASE DE DATOS (Configuración Híbrida: Local vs Nube)
# ==============================================================================

# Intentamos obtener la URL de base de datos de Render (DATABASE_URL)
database_url = config('DATABASE_URL', default=None)

if database_url:
    # SI ESTAMOS EN RENDER (O hay URL en .env): Usamos esa conexión
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # SI ESTAMOS EN TU PC (Y no definiste DATABASE_URL): Usamos configuración manual
    # Esto busca DB_NAME, DB_USER, etc. en tu archivo .env local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }


# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ==============================================================================
# IDIOMA Y ZONA HORARIA
# ==============================================================================
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES)
# ==============================================================================
STATIC_URL = 'static/'

# Carpeta donde se juntarán los archivos al hacer deploy
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Motor de almacenamiento eficiente para Render (WhiteNoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==============================================================================
# REDIRECCIONES DE LOGIN
# ==============================================================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'landing'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'