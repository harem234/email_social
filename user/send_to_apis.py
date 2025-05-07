from user.models import OTPToken

# todo add proper logging to console
def send_otp_to_console(otp_obj: OTPToken):
    print("user pk", otp_obj.user_id)
    print("user otp", otp_obj.otp_token)
