#!/bin/bash
set -e

# Instala dependências
pip install -r requirements.txt

# Entra no diretório do projeto
cd estoque_backend

# Aplica migrações
python manage.py migrate

# Coleta arquivos estáticos (se necessário)
python manage.py collectstatic --noinput

# Inicia o Gunicorn
exec gunicorn estoque_backend.wsgi:application --bind 0.0.0.0:$PORT
