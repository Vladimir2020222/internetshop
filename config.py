import os

SECRET_KEY = os.environ.get('SECRET_KEY')

if SECRET_KEY is None:
    raise RuntimeError('.env file is not activated')

DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
