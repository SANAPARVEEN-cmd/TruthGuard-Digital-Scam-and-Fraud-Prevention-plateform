from django.db.models import Q
from django.shortcuts import render

from .models import Alert


def alerts_list(request):
    severity = request.GET.get('severity', '')
    category = request.GET.get('category', '')
    date_filter = request.GET.get('date', '')

    alerts = Alert.objects.filter(is_active=True)

    if severity:
        alerts = alerts.filter(severity=severity)
    if category:
        alerts = alerts.filter(category=category)
    if date_filter == 'today':
        from django.utils import timezone
        today = timezone.now().date()
        alerts = alerts.filter(created_at__date=today)
    elif date_filter == 'week':
        from django.utils import timezone
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        alerts = alerts.filter(created_at__gte=week_ago)
    elif date_filter == 'month':
        from django.utils import timezone
        from datetime import timedelta
        month_ago = timezone.now() - timedelta(days=30)
        alerts = alerts.filter(created_at__gte=month_ago)

    return render(request, 'alerts/list.html', {
        'alerts': alerts,
        'severity': severity,
        'category': category,
        'date_filter': date_filter,
        'severity_choices': Alert.SEVERITY_CHOICES,
        'category_choices': Alert.CATEGORY_CHOICES,
    })
