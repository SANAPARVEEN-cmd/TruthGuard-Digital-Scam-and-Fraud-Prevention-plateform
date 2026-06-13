from django.urls import path

from .views import report_view, report_success

urlpatterns = [
    path('', report_view, name='report'),
    path('success/', report_success, name='report_success'),
]
