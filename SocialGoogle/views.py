import sys

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.sites.models import Site
from django.views.generic.base import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.db import DatabaseError

from google_auth_oauthlib.flow import Flow

from social.models import SocialAccount, SocialProvider
from social.views import create_social_create_email_user

# TODO add celery priodic task to refresh google's tokens

if hasattr(settings, 'GOOGLE_CLIENT_FILE_PATH'):
    GOOGLE_CLIENT_FILE_PATH = settings.GOOGLE_CLIENT_FILE_PATH
else:
    raise ValueError('GOOGLE_CLIENT_FILE_PATH is required in settings')

if hasattr(settings, 'GOOGLE_CLIENT_FILE_PATH'):
    SCOPES = settings.GOOGLE_CLIENT_SCOPES
else:
    raise ValueError('GOOGLE_CLIENT_SCOPES is required in settings')

GOOGLE_OPTIONS = None

if hasattr(settings, 'GOOGLE_OPTIONS'):
    GOOGLE_OPTIONS = settings.GOOGLE_OPTIONS

GOOGLE_SOCIAL_PROVIDER_ID = SocialProvider.objects.get(social=SocialProvider.GOOGLE).id

# view names that require logged in user
# REQUIRE_LOGGED_IN_URL_NAMES: set = {'google_callback_add_social', 'google_callback_revoke',}

next_call_isauthenticated_set: set[str] = {
    f'google_callback_add_social:{False}', 
    f'google_callback_revoke:{False}',
}

@require_http_methods(["GET", ])
def google_call(request, next_call):
    """
    :param request:
    :param next_call: str
        name of the url what will be called by google.
    """

    # # view names that require logged in user
    # if next_call in REQUIRE_LOGGED_IN_URL_NAMES:
    #     # view require logged in user
    #     if not request.user.is_authenticated:
    #         return redirect_to_login(request.path, login_url=reverse('login'))

    # if callback from google go to a view that require logged in user, and user is not looged in
    # redirect user
    if f'next_call:{not request.user.is_authenticated}' in next_call_isauthenticated_set:
        return redirect_to_login(request.path, login_url=reverse('login'))

    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = None
    try:
        flow = Flow.from_client_secrets_file(GOOGLE_CLIENT_FILE_PATH, SCOPES, )
    except ValueError as err:
        print(err)
        return redirect('google_error')
    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    try:
        # todo any better idea to make the url?
        # request.build_absolute_uri(reverse('view_name', args=(obj.pk, ))) TODO test if works
        flow.redirect_uri = '%s%s' % (request.build_absolute_uri('/')[:-1], reverse(next_call))
    except KeyError as err:
        print(err)
        return redirect('google_error')

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    # Enable incremental authorization. Recommended as a best practice.
    # include_granted_scopes = 'true',
    # login_hint=request.user.is_anonymous or request.user.email,
    # re-prompting the user for permission. Recommended for web server apps.
    # prompt='consent',
    # Enable offline access so that you can refresh an access token without
    # access_type = 'offline',
    
    authorization_url, state = flow.authorization_url(**GOOGLE_OPTIONS)

    return redirect(authorization_url)


@require_http_methods(["GET", ])
@user_passes_test(lambda u: u.is_anonymous, login_url=reverse_lazy('logout'), redirect_field_name='next')
def google_callback_signup(request):

    if 'access_denied' == request.GET.get('error', ''):
        return redirect('google_error')

    state = request.GET.get('state', '')
    code = request.GET.get('code', '')
    redirect_uri = request.GET.get('redirect_uri', request.build_absolute_uri('?'))
    import google_auth_oauthlib.flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_FILE_PATH,
        SCOPES,
        state=state)
    flow.redirect_uri = redirect_uri
    try:
        flow.fetch_token(code=code)
    except Exception as err:
        print("google_callback_signup: ", err)
        print("Unexpected error: ", sys.exc_info()[0])
        return redirect('google_error')

    # obligates https
    # authorization_response = request.build_absolute_uri()
    # flow.fetch_token(authorization_response=authorization_response)

    try:
        idinfo = authorize_by_google_api_profile(flow.credentials.client_id, flow.credentials.id_token, )
        userId = idinfo['sub']
        email = idinfo['email']
        isEmailVerified = idinfo['email_verified']
    except ValueError as err:
        print('google_callback_signup: ', err)
        return redirect('google_error')

    try:
        create_social_create_email_user(userId, email, SocialProvider.objects.get(social=SocialProvider.GOOGLE),
                                        isEmailVerified)
    except ValueError as err:
        print(err)
        return redirect('google_error')

    return redirect('FLEX:index', )


@require_http_methods(["GET", ])
@user_passes_test(lambda u: u.is_anonymous, login_url=reverse_lazy('google'), redirect_field_name=None)
def google_callback_login(request):
    if 'access_denied' == request.GET.get('error', ''):
        return redirect('google_error')

    state = request.GET.get('state', '')
    code = request.GET.get('code', '')
    redirect_uri = request.GET.get('redirect_uri', request.build_absolute_uri('?'))
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_FILE_PATH,
        SCOPES,
        state=state)
    flow.redirect_uri = redirect_uri

    try:
        flow.fetch_token(code=code)
    except Exception as err:
        print("Exception:", err)
        return redirect('google_error')

    # obligates https
    # authorization_response = request.build_absolute_uri()
    # flow.fetch_token(authorization_response=authorization_response)
    idinfo = authorize_by_google_api_profile(flow.credentials.client_id, flow.credentials.id_token, )
    userId = idinfo['sub']
    try:
        account = SocialAccount.objects.get(social_id=userId,
                                            provider=SocialProvider.objects.get(social=SocialProvider.GOOGLE),
                                            site=Site.objects.get_current())
    except SocialAccount.DoesNotExist:
        # there is no user with this social account by the given google user id
        return redirect('google_error')

    # LogIn the user with the social account
    login(request, account.user, )

    return redirect('FLEX:index', )


@require_http_methods(["GET", ])
@user_passes_test(lambda u: u.is_anonymous, login_url=reverse_lazy('logout'), redirect_field_name='next')
def google_callback_login_signup(request):
    """
    @param request:
    @return:

    if Google id is associated with a user log in the user
    if Google id is NOT associated with a user make the user and social account then  log in the user
    """
    if 'access_denied' == request.GET.get('error', ''):
        return redirect('google_error')

    state = request.GET.get('state', '')
    # code = request.GET.get('code', '')
    redirect_uri = request.GET.get('redirect_uri', request.build_absolute_uri('?'))
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_FILE_PATH,
        SCOPES,
        state=state)
    flow.redirect_uri = redirect_uri

    authorization_response = request.get_raw_uri()

    try:
        # flow.fetch_token(code=code)
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as err:
        print("google fetch_token error:", err)
        return redirect('google_error')

    try:
        idinfo = authorize_by_google_api_profile(flow.credentials.client_id, flow.credentials.id_token, )
        userId = idinfo['sub']
        email = idinfo['email']
        isEmailVerified = idinfo['email_verified']
    except ValueError as err:
        print('google_callback_signup: ', err)
        return redirect('google_error')

    account = SocialAccount.objects.filter(
        social_id=userId,
        provider_id=GOOGLE_SOCIAL_PROVIDER_ID,
        site_id=request.site.id).select_related('user').first()

    # if the google id has an account then -> log in the user
    if account and account.user:
         # LogIn the user with the social account
        login(request, account.user, )
        return redirect('FLEX:index', )
    else:
        try:
            emailUser, socialAccount = create_social_create_email_user(
                userId, 
                email, 
                GOOGLE_SOCIAL_PROVIDER_ID,
                isEmailVerified, )
        except ValueError as err:
            print('google_callback_login_signup:', err)
            return redirect('google_error')

        # account = SocialAccount.objects.get(
        #     social_id=userId,
        #     provider_id=GOOGLE_SOCIAL_PROVIDER_ID,
        #     site=Site.objects.get_current(),
        # )

        login(request, emailUser, )

        return redirect('FLEX:index', )


@require_http_methods(["GET", ])
@login_required(login_url=reverse_lazy('login'), redirect_field_name='next')
def google_callback_add_social(request):
    if 'access_denied' == request.GET.get('error', ''):
        return redirect('google_error')

    state = request.GET.get('state', '')
    code = request.GET.get('code', '')
    redirect_uri = request.GET.get('redirect_uri', request.build_absolute_uri('?'))
    import google_auth_oauthlib.flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_FILE_PATH,
        SCOPES,
        state=state)
    flow.redirect_uri = redirect_uri
    try:
        flow.fetch_token(code=code)
    except ValueError as err:
        print("flow.fetch_token: ", err)
        return redirect('google_error')
    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        return redirect('google_error')

    # authorization_response = request.build_absolute_uri()
    # obligates https
    # flow.fetch_token(authorization_response=authorization_response)

    idinfo = authorize_by_google_api_profile(flow.credentials.client_id, flow.credentials.id_token, )
    social_id = idinfo['sub']
    email = idinfo['email']
    # isEmailVerified = idinfo['email_verified']
    try:
        socialAccount, isCreated = SocialAccount.objects.get_or_create(site=Site.objects.get_current(),
                                                                       user=request.user,
                                                                       provider=SocialProvider.objects.get(
                                                                           social=SocialProvider.GOOGLE),
                                                                       defaults={
                                                                           'social_id': social_id, 'is_connected': True,
                                                                           'email': email, })

    except DatabaseError:
        # database error
        return redirect('google_error')
    if isCreated:
        # social account created and added to the user
        return redirect('FLEX:index', )
    else:
        # social account already exist for the user
        return redirect('google_error')


@require_http_methods(["GET", ])
@login_required(login_url=reverse_lazy('login'), redirect_field_name=None)
def google_callback_revoke(request):
    if 'access_denied' == request.GET.get('error', ''):
        return redirect('google_error')

    state = request.GET.get('state', '')
    code = request.GET.get('code', '')
    redirect_uri = request.GET.get('redirect_uri', request.build_absolute_uri('?'))
    import google_auth_oauthlib.flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_FILE_PATH,
        SCOPES,
        state=state)
    flow.redirect_uri = redirect_uri
    try:
        flow.fetch_token(code=code)
    except Exception as err:
        print("google_callback_revoke: ", err)
        print("Unexpected error:", sys.exc_info()[0])
        return redirect('google_error')

    import requests
    requests.post('https://accounts.google.com/o/oauth2/revoke',
                  params={'token': flow.credentials.token},
                  headers={'content-type': 'application/x-www-form-urlencoded'})
    return redirect('FLEX:index', )


"""
the following is used by the javascript version of the google api
"""


@method_decorator(ensure_csrf_cookie, name='dispatch')
class TemplateCSRFView(TemplateView):
    """A view for loading google javascript api and ajax json post by xhr to post
     the view always send csrf token along responds(means there is no need for {% csrf token %})"""
    template_name = 'SocialGoogle/google_api.html'

    # extra_context = {'client_id': SocialProvider.objects.get(social=SocialProvider.GOOGLE).client_id, }

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if 'client_id' not in data:
            data['client_id'] = SocialProvider.objects.get(social=SocialProvider.GOOGLE).client_id
        return data


class AjaxJsonGoogleMixin:
    """
    Mixin for AJAX support json.

    request.is_ajax()
    https://docs.djangoproject.com/en/2.2/ref/request-response/#django.http.HttpRequest.is_ajax
    Returns True if the request was made via an XMLHttpRequest, by checking the HTTP_X_REQUESTED_WITH header for the string 'XMLHttpRequest'
    """
    id_token = None

    # We make sure to call the parent's form_valid() method because
    # it might do some processing (in the case of CreateView, it will
    # call form.save() for example).
    def get_id_token(self, request):
        from django.http import JsonResponse
        if request.is_ajax():  # request.method == POST and HTTP_X_REQUESTED_WITH == 'XMLHttpRequest'
            import json
            self.id_token = json.loads(request.body)['id_token']
            if self.id_token:
                return True
            else:
                return JsonResponse({'status': 'false', 'error': 'denied by google'}, status=400)
        else:
            return JsonResponse({'status': 'false', 'error': 'not ajax'}, status=400)


class AjaxGoogleAuthorizeMixin(AjaxJsonGoogleMixin):
    idinfo = None

    def get_id_info(self, request):
        if super().get_id_token(request):
            # authenticate google id_token
            # google id_token is valid go to index page
            self.idinfo = authorize_by_google_api_profile(
                SocialProvider.objects.get(social=SocialProvider.GOOGLE).client_id, self.id_token)
            return True

        # authentication failed
        from django.http import JsonResponse
        return JsonResponse({'status': 'false', 'error': 'denied by google'}, status=400)


decorators = [require_http_methods(["POST", ]),
              user_passes_test(lambda u: u.is_anonymous, login_url=reverse_lazy('google'),
                               redirect_field_name=None), ]


@method_decorator(decorators, name='dispatch')
class GoogleAjaxSignupView(AjaxGoogleAuthorizeMixin, View):

    def post(self, request):
        if super().get_id_info(request):
            userId = self.idinfo.get('sub', None)
            email = self.idinfo.get('email', None)
            isEmailVerified = self.idinfo.get('email_verified', None)
            try:
                from social.views import create_social_create_email_user
                create_social_create_email_user(userId, email,
                                                SocialProvider.objects.get(social=SocialProvider.GOOGLE),
                                                isEmailVerified)
            except ValueError as err:
                print(err)
                return JsonResponse({'status': 'false', 'error': 'already exist'}, status=400)
        else:
            return JsonResponse({'status': 'false', 'error': 'denied by google'}, status=400)
        return JsonResponse({'status': 'ok', }, status=200)


decorators = [require_http_methods(["POST", ])]


@method_decorator(decorators, name='dispatch')
class GoogleAjaxLoginView(AjaxGoogleAuthorizeMixin, View):
    def post(self, request):
        if super().get_id_info(request):
            userId = self.idinfo.get('sub', None)
            try:
                account = SocialAccount.objects.get(social_id=userId,
                                                    provider=SocialProvider.objects.get(
                                                        social=SocialProvider.GOOGLE),
                                                    site=Site.objects.get_current())
            except SocialAccount.DoesNotExist:
                # there is no user with this social account by the given google user id
                return JsonResponse({'status': 'false', 'error': 'account not found'}, status=400)

            # LogIn the user with the social account
            login(request, account.user, )

            return JsonResponse({'status': 'ok'}, status=200)


decorators = [require_http_methods(["POST", ]),
              login_required(login_url=reverse_lazy('login'), )]


@method_decorator(decorators, name='dispatch')
class GoogleAjaxAddSocialView(AjaxGoogleAuthorizeMixin, View):

    def post(self, request):
        if super().get_id_info(request):
            userId = self.idinfo.get('sub', None)
            email = self.idinfo.get('email', None)
            isEmailVerified = self.idinfo.get('email_verified', None)

            try:
                socialAccount, isCreated = SocialAccount.objects.get_or_create(site=Site.objects.get_current(),
                                                                               user=request.user,
                                                                               provider=SocialProvider.objects.get(
                                                                                   social=SocialProvider.GOOGLE),
                                                                               defaults={
                                                                                   'social_id': userId,
                                                                                   'is_connected': True,
                                                                                   'email': email, })
            except DatabaseError as err:
                # database error
                print('GoogleAjaxAddSocial', err)
                return JsonResponse({'status': 'false', 'error': ''}, status=400)

            if isCreated:
                # social account created and added to the user
                return JsonResponse({'status': 'ok'}, status=200)
            else:
                # social account already exist for the user
                return JsonResponse({'status': 'false', 'error': 'account exist'}, status=400)


"""
    the latter functions to exchange credentials for user information
"""


def authorize_by_google_api_profile(client_id, token):
    from google.oauth2 import id_token
    from google.auth.transport import requests

    idinfo = None
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.

    except ValueError as er:
        # Invalid token
        print('authorize_by_google_api_profile: ', er)
        return None

    return idinfo
