from django.urls import path

from .views import search_view, entity_detail

urlpatterns = [
    path('', search_view, name='search'),
    path('<int:pk>/', entity_detail, name='entity_detail'),
]
