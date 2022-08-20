from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, TemplateView
from django.views import View
from django.template.loader import render_to_string
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views, get_user_model
from django.contrib.auth.tokens import default_token_generator

from .forms import CustomUserCreationForm

User = get_user_model()


@method_decorator(require_http_methods(("POST",)), name='dispatch')
class PostLogoutView(views.LogoutView):
    """
    only with Post request user can log out,
    this adds more security.
    """
    next_page = reverse_lazy('logout_post')

    # @method_decorator(require_http_methods(["POST", ]))
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    # model object
    # context_object_name = 'signup_model'

    # form instance name in context
    # context_form_name = 'signup_form'


class CustomLoginView(LoginView):
    template_name = 'registration/password_change_form.html'
    extra_context = {'next': reverse_lazy('index')}


@method_decorator(login_required(login_url=reverse_lazy('login')), name='dispatch', )
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')


@method_decorator(login_required(login_url=reverse_lazy('login')), name='dispatch', )
class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


@method_decorator(require_http_methods(('POST', 'GET')), name='dispatch')
@method_decorator(login_required(login_url=reverse_lazy('login')), name='post', )
class VerifyEmailView(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        # validate users email

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save()
            return HttpResponse('Thank you for your email confirmation.')
        else:
            return HttpResponse('Activation link is invalid!')

    def post(self, request, *args, **kwargs):
        # send an email to user's email address

        uid = urlsafe_base64_encode(force_bytes(request.user.pk))
        token = default_token_generator.make_token(request.user)

        template_context = {
            'uid': uid,
            'token': token,
        }

        email_body = render_to_string(
            'registration/in_email_request_verify_email.html',
            request=request,
            context=template_context,
        )

        send_mail(_('verify email'), email_body, 'localhost@gmail.com', (request.user.email,))
        return HttpResponse('Please confirm your email address to complete the registration')
