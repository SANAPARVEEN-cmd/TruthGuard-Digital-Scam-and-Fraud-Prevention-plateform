from alerts.models import Alert
from entities.models import Entity
from reports.models import Report


def site_stats(request):
    return {
        'total_reports': Report.objects.filter(report_status='approved').count(),
        'total_entities': Entity.objects.count(),
        'active_alerts': Alert.objects.filter(is_active=True).count(),
        'high_risk_entities': Entity.objects.filter(threat_level__in=['high', 'critical']).count(),
    }
