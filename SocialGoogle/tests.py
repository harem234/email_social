from django.test import TestCase
from django.urls import reverse

call_back_url_names = ['google_callback_signup', 'google_callback_login', 'google_callback_add_social',
                       'google_callback_revoke', ]


class TestPages(TestCase):
    def test_google_api_callback(self):
        for call in call_back_url_names:
            response = self.client.get(reverse('google_call', kwargs={'next_call': call}))
            self.assertEqual(response.status_code, 302)
