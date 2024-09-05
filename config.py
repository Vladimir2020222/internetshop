import os

SECRET_KEY = os.environ.get('SECRET_KEY')

if SECRET_KEY is None:
    raise RuntimeError('.env file is not activated')

DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

JWT_ENCODE_ALGORITHM = 'HS256'
DECODE_JWT_ALGORITHMS = ['HS256']

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
