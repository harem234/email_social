# OTP token generator
# import library
import math
import random

from user.models import OTPToken


# function to generate OTP token
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

