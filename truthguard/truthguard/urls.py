from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'TruthGuard Admin'
admin.site.site_title = 'TruthGuard'
admin.site.index_title = 'Fraud Intelligence Control Panel'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('search/', include('entities.urls')),
    path('report/', include('reports.urls')),
    path('alerts/', include('alerts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
