#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# --- AGREGA ESTA LÍNEA AL FINAL ---
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@tuempresa.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('El usuario admin ya existe')"
