from django.urls import path
from django.views.generic import TemplateView

app_name = 'ALST'

urlpatterns = [
    path('index/', TemplateView.as_view(template_name='ALSTAR/index.html'), name='index'),
]
