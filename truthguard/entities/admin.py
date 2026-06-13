from django.contrib import admin

from .models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = (
        'entity_value', 'entity_type', 'risk_score', 'threat_level',
        'status', 'report_count', 'updated_at',
    )
    list_filter = ('entity_type', 'threat_level', 'status')
    search_fields = ('entity_value',)
    readonly_fields = ('risk_explanation', 'created_at', 'updated_at')
    ordering = ('-risk_score',)
