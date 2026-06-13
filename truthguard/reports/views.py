from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from analytics.services.risk_engine import risk_engine
from reports.forms import ReportForm
from entities.models import Entity
from entities.utils import normalize_value
from .models import Report


@require_http_methods(['GET', 'POST'])
def report_view(request):
    form = ReportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        entity_type = form.cleaned_data['entity_type']
        entity_value = form.cleaned_data['entity_value']
        description = form.cleaned_data['description']
        evidence = form.cleaned_data.get('evidence')

        entity, _ = Entity.objects.get_or_create(
            entity_type=entity_type,
            entity_value=entity_value,
        )

        Report.objects.create(
            reporter=request.user if request.user.is_authenticated else None,
            entity=entity,
            description=description,
            evidence=evidence,
            report_status='pending',
        )

        risk_engine.update_entity(entity)
        messages.success(
            request,
            'Report submitted successfully. Our team will review it shortly.',
        )
        return redirect('report_success')

    return render(request, 'reports/report.html', {'form': form})


def report_success(request):
    return render(request, 'reports/success.html')
