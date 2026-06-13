import json
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from alerts.models import Alert
from entities.models import Entity
from reports.models import Report


def dashboard_view(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    stats = {
        'total_reports': Report.objects.filter(report_status='approved').count(),
        'total_entities': Entity.objects.count(),
        'active_alerts': Alert.objects.filter(is_active=True).count(),
        'high_risk': Entity.objects.filter(threat_level__in=['high', 'critical']).count(),
        'pending_reports': Report.objects.filter(report_status='pending').count(),
        'safe_entities': Entity.objects.filter(threat_level='safe').count(),
    }

    threat_distribution = list(
        Entity.objects.values('threat_level')
        .annotate(count=Count('id'))
        .order_by('threat_level')
    )

    entity_type_distribution = list(
        Entity.objects.values('entity_type')
        .annotate(count=Count('id'))
        .order_by('entity_type')
    )

    reports_timeline = list(
        Report.objects.filter(created_at__gte=week_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    alert_severity = list(
        Alert.objects.filter(is_active=True)
        .values('severity')
        .annotate(count=Count('id'))
    )

    high_risk_entities = Entity.objects.filter(
        threat_level__in=['high', 'critical']
    ).order_by('-risk_score')[:10]

    recent_activity = Report.objects.select_related(
        'entity', 'reporter'
    ).order_by('-created_at')[:10]

    recent_alerts = Alert.objects.filter(is_active=True).order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'threat_distribution': json.dumps(threat_distribution),
        'entity_type_distribution': json.dumps(entity_type_distribution),
        'reports_timeline': json.dumps([
            {'date': str(item['date']), 'count': item['count']}
            for item in reports_timeline
        ]),
        'alert_severity': json.dumps(alert_severity),
        'high_risk_entities': high_risk_entities,
        'recent_activity': recent_activity,
        'recent_alerts': recent_alerts,
    }
    return render(request, 'dashboard/index.html', context)
