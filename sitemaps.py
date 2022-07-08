from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.4
    changefreq = 'daily'

    def items(self):
        return (
            "FLEX:about",
            "FLEX:contact",
            "FLEX:errorpage",
            "FLEX:features",
            "FLEX:pricing",
            "FLEX:pricing_light",
            "FLEX:projects",
            "FLEX:team",
            "FLEX:index",
            "FLEX:logout",
            "FLEX:login",
            "FLEX:signup",
            "FLEX:password_change",
            "FLEX:password_change_done",
        )

    def location(self, item):
        return reverse(item)
