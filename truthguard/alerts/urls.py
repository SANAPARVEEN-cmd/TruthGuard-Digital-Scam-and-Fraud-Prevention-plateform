from django.urls import path

from .views import alerts_list

urlpatterns = [
    path('', alerts_list, name='alerts'),
]
