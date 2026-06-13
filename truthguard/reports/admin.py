from django.contrib import admin, messages

from analytics.services.risk_engine import risk_engine
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('entity', 'reporter', 'report_status', 'created_at')
    list_filter = ('report_status', 'created_at')
    search_fields = ('entity__entity_value', 'description', 'reporter__username')
    readonly_fields = ('created_at',)
    actions = ['approve_reports', 'reject_reports']

    @admin.action(description='Approve selected reports')
    def approve_reports(self, request, queryset):
        count = 0
        for report in queryset.filter(report_status='pending'):
            report.report_status = 'approved'
            report.save()
            if report.reporter and hasattr(report.reporter, 'profile'):
                profile = report.reporter.profile
                profile.total_reports += 1
                profile.reputation_score = min(profile.reputation_score + 5, 100)
                profile.save()
            risk_engine.update_entity(report.entity)
            count += 1
        self.message_user(request, f'{count} report(s) approved.', messages.SUCCESS)

    @admin.action(description='Reject selected reports')
    def reject_reports(self, request, queryset):
        count = queryset.filter(report_status='pending').update(report_status='rejected')
        for report in queryset:
            risk_engine.update_entity(report.entity)
        self.message_user(request, f'{count} report(s) rejected.', messages.WARNING)
