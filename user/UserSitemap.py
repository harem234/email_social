from django.contrib.sitemaps import Sitemap
from user.models import EmailUser

class UserSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return EmailUser.objects.filter(is_staff=False, is_active=True).order_by('id')

    def lastmod(self, obj):
        return obj.date_joined