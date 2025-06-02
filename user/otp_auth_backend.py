from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from user.models import OTPToken

UserModel = get_user_model()


class OTPTokenBackend(ModelBackend):


    def authenticate(self, request, mobile_phone=None, otp_token=None, **kwargs):

        if mobile_phone is None:
            mobile_phone = kwargs.get(UserModel.MOBILE_FIELD)

        if mobile_phone is None or otp_token is None:
            return None

        try:
            user = UserModel._default_manager.get_by_natural_key(mobile_phone)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(otp_token)
            return None
        else:
            if OTPToken.check_otp_token(user.pk, otp_token, ) and self.user_can_authenticate(user):
                return user

            return None

    async def aauthenticate(self, request, mobile_phone=None, otp_token=None, **kwargs):

        if mobile_phone is None:
            mobile_phone = kwargs.get(UserModel.MOBILE_FIELD)

        if mobile_phone is None or otp_token is None:
            return None
        try:
            user = await UserModel._default_manager.get_by_natural_key(mobile_phone)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(otp_token)
            return None
        else:
            if (
                    await OTPToken.acheck_otp_token_and_can_authenticate(user.pk, otp_token, )
                    and
                    self.user_can_authenticate(user)
            ):
                return user
            return None

    def user_can_authenticate(self, user):
        # """
        # Reject users with is_active=False. Custom user models that don't have
        # that attribute are allowed.
        # """
        return getattr(user, "is_active", True)
