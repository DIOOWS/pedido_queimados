#!/bin/bash
python manage.py migrate
python manage.py shell < create_admin.py
gunicorn requisicoes.wsgi:application
