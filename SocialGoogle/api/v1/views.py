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
REQUIRE_LOGGED_IN_URL_NAMES: set = {'google_callback_add_social', 'google_callback_revoke',}


@require_http_methods(["GET", ])
def google_call(request, next_call):
    """
    :param request:
    :param next_call: str
        name of the url what will be called by google.
    """
    # view names that require logged in user
    if next_call in REQUIRE_LOGGED_IN_URL_NAMES:
        # view require logged in user
        if not request.user.is_authenticated:
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

    return JsonResponse({'redirect': authorization_url}, )