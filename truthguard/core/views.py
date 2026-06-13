from django.shortcuts import render

from alerts.models import Alert
from entities.models import Entity
from reports.models import Report


def home(request):
    latest_alerts = Alert.objects.filter(is_active=True).order_by('-created_at')[:4]
    stats = {
        'total_reports': Report.objects.filter(report_status='approved').count(),
        'total_entities': Entity.objects.count(),
        'active_alerts': Alert.objects.filter(is_active=True).count(),
        'risk_detections': Entity.objects.filter(threat_level__in=['high', 'critical']).count(),
    }
    return render(request, 'core/home.html', {
        'latest_alerts': latest_alerts,
        'stats': stats,
    })
