from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from analytics.services.risk_engine import risk_engine
from entities.forms import SearchForm
from entities.models import Entity
from entities.utils import detect_entity_type, normalize_value
from reports.models import Report


@require_http_methods(['GET', 'POST'])
def search_view(request):
    form = SearchForm(request.POST or None)
    entity = None
    risk_result = None
    historical_reports = []
    related_alerts = []

    if request.method == 'POST' and form.is_valid():
        query = form.cleaned_data['query']
        entity_type = form.get_entity_type() or detect_entity_type(query)

        if not entity_type:
            messages.warning(request, 'Could not detect entity type. Try a phone, email, or URL.')
        else:
            normalized = normalize_value(entity_type, query)
            entity, created = Entity.objects.get_or_create(
                entity_type=entity_type,
                entity_value=normalized,
                defaults={'status': 'monitoring'},
            )
            risk_result = risk_engine.update_entity(entity)
            historical_reports = Report.objects.filter(
                entity=entity,
                report_status='approved',
            ).select_related('reporter')[:10]
            related_alerts = entity.alerts.filter(is_active=True)[:5]

            if created and risk_result['risk_score'] == 0:
                messages.info(request, 'Entity not found in threat database. Risk score is low.')

    return render(request, 'entities/search.html', {
        'form': form,
        'entity': entity,
        'risk_result': risk_result,
        'historical_reports': historical_reports,
        'related_alerts': related_alerts,
    })


def entity_detail(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    risk_result = risk_engine.calculate(entity)
    historical_reports = Report.objects.filter(
        entity=entity,
        report_status='approved',
    ).select_related('reporter')
    related_alerts = entity.alerts.filter(is_active=True)
    return render(request, 'entities/detail.html', {
        'entity': entity,
        'risk_result': risk_result,
        'historical_reports': historical_reports,
        'related_alerts': related_alerts,
    })
