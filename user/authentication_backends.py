from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from user.models import OTPToken

User = get_user_model()


def check_otp_token_and_authenticate_redis(otp_token, user):
    """

    @param otp_token:
    @param user:

    @return: true on validating otp token
    """


class OTPTokenBackend(ModelBackend):

    def user_can_authenticate(self, user):
        # already checked by user.models.OTPToken.check_otp_token_and_authentication function as part of the query
        pass

        # """
        # Reject users with is_active=False. Custom user models that don't have
        # that attribute are allowed.
        # """
        # return getattr(user, "is_active", True)

    def authenticate(self, request, mobile_phone=None, otp_token=None, **kwargs):

        try:
            user = User.objects.get(mobile_phone=mobile_phone)
        except User.DoesNotExist:
            return None
        else:
            if OTPToken.check_otp_token_and_authentication(user.pk, otp_token, ):
                return user

    def get_user(self, user_id):

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
