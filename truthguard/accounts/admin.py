from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0
    readonly_fields = ('created_at',)


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'is_staff', 'get_reputation', 'get_reports', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    @admin.display(description='Reputation')
    def get_reputation(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.reputation_score
        return '-'

    @admin.display(description='Reports')
    def get_reports(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.total_reports
        return '-'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'reputation_score', 'total_reports', 'verified_status', 'created_at')
    list_filter = ('verified_status',)
    search_fields = ('user__username', 'user__email')
    list_editable = ('reputation_score', 'verified_status')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
