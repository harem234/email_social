"""DJ_EmailUser_Social URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView

from sitemaps import StaticViewSitemap

# visit http://this_project_domain/sitemap.xml to check site map
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('flex/', include('flexart.urls')),
    path('accounts/', include('user.urls')),
    path('', include('SocialGoogle.urls')),
    path('admin/', admin.site.urls),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='sitemap',
    ),
    path('google813daf404e148806.html',
         TemplateView.as_view(template_name='google813daf404e148806.html')
    ),
]
