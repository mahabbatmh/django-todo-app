from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail

from todoapp.celery import app

logger = logging.getLogger('Celery')


@app.task
def send_notification(*args):
    subject = args[0]
    message =args[1]
    recipient_list = args[2]
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject=subject, message=message, from_email=email_from, recipient_list=recipient_list)
    logger.info("Email sent to {0} at {1}".format(*recipient_list, datetime.now()))
