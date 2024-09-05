from celery.signals import worker_shutdown, worker_init

from celery_app import celery_app
import mail


worker_init.connect(mail.init_smtp)
worker_shutdown.connect(mail.quit_smtp)
