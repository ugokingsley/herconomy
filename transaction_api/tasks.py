import dateutil.parser
import datetime
import requests
from celery import shared_task
from django.core.mail import send_mail
#from redismail import settings
from django.conf import settings
from django.core.mail import EmailMessage

from .models import *


@shared_task(bind=True)
def send_notification_mail(self, target_mail, message):
    # this will be used to send mail to users
    # with message relating to policies
    email = EmailMessage(
                subject='Notification from Herconomy.com !',
                body= message,
                to=[target_mail]
                )
    email.send(fail_silently=True)
    return {'status': 'sent successfully'}