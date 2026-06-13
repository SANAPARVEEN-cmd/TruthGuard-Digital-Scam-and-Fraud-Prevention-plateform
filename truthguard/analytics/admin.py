from django.contrib import admin

from .models import Pattern


@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ('pattern_name', 'signature', 'risk_weight', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('pattern_name', 'signature')
    filter_horizontal = ('related_entities',)
