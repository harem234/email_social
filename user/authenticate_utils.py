import math
import random
from django.conf import settings
import logging

logger = logging.getLogger('django')


def generate_otp():
    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    otp_token = ""

    # length of password can be changed
    # by changing value in range
    for i in range(8):
        otp_token += digits[math.floor(random.random() * 10)]

    return otp_token

def send_otp_token(otp_obj):
    if getattr(settings, 'LOCAl_OTP_SMS', False) is True:
        # warning on debug mode false
        # print(otp_obj.otp_token)
        logger.info(otp_obj.otp_token)
    else:
        # todo add sms api
        pass

