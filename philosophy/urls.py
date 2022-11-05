from django.urls import path
from django.views.generic import TemplateView

app_name = 'PHILOS'
urlpatterns = [
    path('index/', TemplateView.as_view(template_name='philosophy/index.html'), name='index'),
    path('style-guide/', TemplateView.as_view(template_name='philosophy/style-guide.html'), name='style-guide'),
    path('about/', TemplateView.as_view(template_name='philosophy/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='philosophy/contact.html'), name='contact'),
    path('category/', TemplateView.as_view(template_name='philosophy/category.html'), name='category'),
    path('single-audio/', TemplateView.as_view(template_name='philosophy/single-audio.html'), name='single-audio'),
    path('single-gallery/', TemplateView.as_view(template_name='philosophy/single-gallery.html'),
         name='single-gallery'),
    path('single-standard/', TemplateView.as_view(template_name='philosophy/single-standard.html'),
         name='single-standard'),
    path('single-video/', TemplateView.as_view(template_name='philosophy/single-video.html'), name='single-video'),

]
