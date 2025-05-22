import random
from django.conf import settings
import logging

LOGGER = logging.getLogger(__name__)


def send_otp_token_local(otp_obj):
    # warning on debug mode false
    # print(otp_obj.otp_token)
    # LOGGER.info(otp_obj.otp_token)
    print(otp_obj)

def send_otp_token_third_party_api(otp_obj):
    pass #TODO

def otp_token_send_mode():

    local_otp_sms = getattr(settings, 'DEBUG') # TODO load LOCAl_OTP_SMS some how at module loading
    print(__name__, 'LOCAl_OTP_SMS', '==', local_otp_sms)

    if local_otp_sms:

        def send_otp_token(otp_obj):
            send_otp_token_local(otp_obj)
    else:

        def send_otp_token(otp_obj):
            send_otp_token_third_party_api(otp_obj)

    return send_otp_token

send_otp_token = otp_token_send_mode()

send_otp_token('123456789_123')

def generate_otp():

    # length of password can be changed
    otp_token = random.randint(100_000_000, 999_999_999)

    return otp_token





