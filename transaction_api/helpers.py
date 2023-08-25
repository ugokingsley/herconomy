import os, math, requests, io, csv
import json
import pytz
import random
import datetime
from rest_framework.response import Response

transaction_id = math.floor(random.random()*9000)

now1 = datetime.datetime.now(pytz.timezone('Africa/Lagos'))
nw = int(now1.strftime("%Y%m%d%H%M%S"))
now = str(nw) + str(random.randint(10001, 99999))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip