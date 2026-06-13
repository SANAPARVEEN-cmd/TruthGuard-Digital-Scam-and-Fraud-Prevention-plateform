from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'category', 'is_active', 'created_at')
    list_filter = ('severity', 'category', 'is_active')
    search_fields = ('title', 'description')
    filter_horizontal = ('related_entities',)
    list_editable = ('is_active',)
