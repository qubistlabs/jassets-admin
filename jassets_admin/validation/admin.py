from django.contrib import admin

from .models import AssetHistory


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
        'symbol',)
    list_filter = (
        'type',
        'is_active',
        'created',
        'updated',
    )
    list_per_page = 25


admin.site.register(AssetHistory, AssetHistoryAdmin)
