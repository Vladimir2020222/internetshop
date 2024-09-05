from celery import Celery


celery_app = Celery(
    'internetshop',
    broker='pyamqp://guest:guest@localhost:5672//',
)
