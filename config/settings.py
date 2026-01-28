from pathlib import Path
import os
import dj_database_url  # <--- Necesario para la base de datos en la nube
from decouple import config  # <--- ¡ESTA ES LA QUE TE FALTA!

# ... (resto de imports)

BASE_DIR = Path(__file__).resolve().parent.parent


# MIDDLEWARE: Agrega WhiteNoise justo después de SecurityMiddleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- AQUÍ (Nuevo)
    # ... resto
]

# BASE DE DATOS: Configuración Híbrida
# Si existe DATABASE_URL (Nube), usa eso. Si no, usa lo de tu .env local (PC)
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # Tu configuración local actual (Postgres local o SQLite)
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

# STATIC FILES (Para que se vean los estilos en la nube)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'