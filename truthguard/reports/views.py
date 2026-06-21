from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from alerts.service import create_or_update_alert

from analytics.services.risk_engine import risk_engine
from reports.forms import ReportForm
from entities.models import Entity
from entities.utils import normalize_value
from .models import Report


# ── Helper: is the user a moderator (staff or superuser)? ─────────────────────
def is_moderator(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ── 1. Submit a report ────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def report_view(request):
    form = ReportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        entity_type  = form.cleaned_data['entity_type']
        entity_value = form.cleaned_data['entity_value']
        description  = form.cleaned_data['description']
        evidence     = form.cleaned_data.get('evidence')

        # Normalise before storing
        normalized = normalize_value(entity_type, entity_value)

        entity, _ = Entity.objects.get_or_create(
            entity_type=entity_type,
            entity_value=normalized,
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


# ── 2. Success page ───────────────────────────────────────────────────────────
def report_success(request):
    return render(request, 'reports/success.html')


# ── 3. My Reports — shows all reports by logged-in user WITH evidence images ──
@login_required
@login_required
def my_reports(request):
    reports = (
        Report.objects
        .filter(reporter=request.user)
        .select_related('entity')
        .order_by('-created_at')
    )
    paginator = Paginator(reports, 10)
    page      = paginator.get_page(request.GET.get('page'))

    # ✅ Add this line
    pending_count = Report.objects.filter(report_status='pending').count() if request.user.is_staff else 0

    return render(request, 'reports/my_reports.html', {
        'page_obj': page,
        'pending_reports_count': pending_count,   # ✅ pass to template
    })

# ── 4. Report detail — shows full info + evidence image/file ─────────────────
@login_required
def report_detail(request, pk):
    # Owner OR moderator can view
    report = get_object_or_404(Report, pk=pk)
    if report.reporter != request.user and not is_moderator(request.user):
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('my_reports')
    return render(request, 'reports/report_detail.html', {'report': report})


# ── 5. Moderator: pending reports queue ──────────────────────────────────────
@login_required
@user_passes_test(is_moderator, login_url='home')
def moderation_queue(request):
    pending  = Report.objects.filter(report_status='pending').select_related('entity', 'reporter').order_by('-created_at')
    approved = Report.objects.filter(report_status='approved').select_related('entity', 'reporter').order_by('-created_at')[:20]
    rejected = Report.objects.filter(report_status='rejected').select_related('entity', 'reporter').order_by('-created_at')[:20]
    return render(request, 'reports/moderation_queue.html', {
        'pending':  pending,
        'approved': approved,
        'rejected': rejected,
    })


# ── 6. Moderator: approve a single report ────────────────────────────────────
# ── ADD this import at the top of reports/views.py ───────────────────────────
# from alerts.services import create_or_update_alert, deactivate_alerts_for_entity


# ── REPLACE your approve_report view with this ────────────────────────────────
@login_required
@user_passes_test(is_moderator, login_url='home')
@require_http_methods(['POST'])
def approve_report(request, pk):
    report = get_object_or_404(Report, pk=pk, report_status='pending')
    report.report_status = 'approved'
    report.save()

    # Boost reporter reputation
    if report.reporter and hasattr(report.reporter, 'profile'):
        profile = report.reporter.profile
        profile.total_reports    = getattr(profile, 'total_reports', 0) + 1
        profile.reputation_score = min(getattr(profile, 'reputation_score', 0) + 5, 100)
        profile.save()

    # Recalculate risk score
    risk_engine.update_entity(report.entity)

    # ✅ Auto-create or update alert based on new risk score
    from alerts.service import create_or_update_alert
    create_or_update_alert(report.entity, report=report)

    messages.success(request, f'Report #{pk} approved. Risk score and alerts updated.')
    return redirect('moderation_queue')


# ── REPLACE your reject_report view with this ────────────────────────────────
@login_required
@user_passes_test(is_moderator, login_url='home')
@require_http_methods(['POST'])
def reject_report(request, pk):
    report = get_object_or_404(Report, pk=pk, report_status='pending')
    report.report_status = 'rejected'
    report.save()

    # Recalculate risk — may lower score if this was the only report
    risk_engine.update_entity(report.entity)

    # ✅ Deactivate alert if entity is now safe after rejection
    from alerts.service import create_or_update_alert
    create_or_update_alert(report.entity)

    messages.warning(request, f'Report #{pk} rejected. Alert status updated.')
    return redirect('moderation_queue')


# ── REPLACE your bulk_moderate view with this ────────────────────────────────
@login_required
@user_passes_test(is_moderator, login_url='home')
@require_http_methods(['POST'])
def bulk_moderate(request):
    from alerts.service import create_or_update_alert
    action     = request.POST.get('action')
    report_ids = request.POST.getlist('report_ids')

    if not report_ids:
        messages.warning(request, 'No reports selected.')
        return redirect('moderation_queue')

    reports = Report.objects.filter(pk__in=report_ids, report_status='pending')

    if action == 'approve':
        count = 0
        for report in reports:
            report.report_status = 'approved'
            report.save()
            if report.reporter and hasattr(report.reporter, 'profile'):
                profile = report.reporter.profile
                profile.total_reports    = getattr(profile, 'total_reports', 0) + 1
                profile.reputation_score = min(getattr(profile, 'reputation_score', 0) + 5, 100)
                profile.save()
            risk_engine.update_entity(report.entity)
            # ✅ Auto-create/update alert
            create_or_update_alert(report.entity, report=report)
            count += 1
        messages.success(request, f'{count} report(s) approved. Alerts updated.')

    elif action == 'reject':
        for report in reports:
            report.report_status = 'rejected'
            report.save()
            risk_engine.update_entity(report.entity)
            create_or_update_alert(report.entity)
        messages.warning(request, f'{reports.count()} report(s) rejected.')
    else:
        messages.error(request, 'Invalid action.')

    return redirect('moderation_queue')