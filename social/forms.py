# from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


# class AddSocialCreateEmailUserForm(UserCreationForm):
#     class Meta:
#         model = get_user_model()
#         fields = ('username',)
#
#
# class EmailUserAuthenticationPasswordLessForm(AuthenticationForm):
#     def clean(self):
#         username = self.cleaned_data.get('username')
#         """
#         [deleted]
#         password = self.cleaned_data.get('password')
#
#         [rewritten]
#         if username is not None and password:
#             self.user_cache = authenticate(self.request, username=username, password=password)
#             if self.user_cache is None:
#                 raise self.get_invalid_login_error()
#             else:
#                 self.confirm_login_allowed(self.user_cache)
#         """
#         if username is not None:
#             self.user_cache = get_user_model().objects.get(username=username)
#             if self.user_cache is None:
#                 raise self.get_invalid_login_error()
#             else:
#                 self.confirm_login_allowed(self.user_cache)
#
#         return self.cleaned_data
