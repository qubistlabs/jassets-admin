from django.contrib import admin

from .models import AssetHistory, ValidationQueue


class AssetHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'uuid',
        'name',
        'symbol',
        'type',
        'is_active',
        'address',
        'properties',
        'created',
        'updated',
    )
    search_fields = (
        'name',
        'symbol',
    )
    list_filter = (
        'type',
        'is_active',
        'created',
        'updated',
    )
    list_per_page = 25


class ValidationQueueAdmin(admin.ModelAdmin):
    list_display = (
        'task_uuid',
        'asset_uuid',
        'method',
    )
    search_fields = (
        'task_uuid',
        'asset_uuid',
        'method',
    )
    list_per_page = 25

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(AssetHistory, AssetHistoryAdmin)
admin.site.register(ValidationQueue, ValidationQueueAdmin)
