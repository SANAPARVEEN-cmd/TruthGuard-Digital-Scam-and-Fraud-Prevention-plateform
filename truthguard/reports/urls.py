from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('',          views.report_view,    name='report'),
    path('success/',  views.report_success, name='report_success'),

    # Authenticated user
    path('my/',            views.my_reports,    name='my_reports'),
    path('my/<int:pk>/',   views.report_detail, name='report_detail'),

    # Moderator / staff only
    path('moderate/',               views.moderation_queue, name='moderation_queue'),
    path('moderate/<int:pk>/approve/', views.approve_report, name='approve_report'),
    path('moderate/<int:pk>/reject/',  views.reject_report,  name='reject_report'),
    path('moderate/bulk/',          views.bulk_moderate,    name='bulk_moderate'),
]