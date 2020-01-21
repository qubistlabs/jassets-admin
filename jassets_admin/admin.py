from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.postgres import fields

from django_json_widget.widgets import JSONEditorWidget

from .validation.admin_actions import get_validation_actions, collect_links
from .models import TradingPair, Platform, Asset, Exchange, AssetLink
from .files.admin import AssetAttachmentInline


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 25


class PlatformAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'name',
        'symbol',
        'main_asset_obj',
    )
    list_select_related = (
        'main_asset_obj',
    )
    search_fields = (
        'name',
        'symbol',
    )
    list_filter = (
        'main_asset_obj__type',
        'main_asset_obj__is_active',
    )


class AssetLinkAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'asset_obj',
        'type',
        'url',
    )
    list_filter = (
        'asset_obj',
    )


class AssetLinkInline(TabularInline):
    model = AssetLink
    extra = 1


class AssetAdmin(BaseModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }

    list_display = (
        'id',
        'uuid',
        'name',
        'platform_obj',

        'validation_status',
        'symbol',
        'type',
        'is_active',
        'address',
        'properties',

        'created',
        'updated',
    )
    list_select_related = (
        'platform_obj',
    )
    search_fields = (
        'name',
        'symbol',
        'uuid',
        'address',
    )
    list_filter = (
        'platform_obj',
        'type',
        'is_active',
        'created',
        'updated',
    )

    actions = [collect_links] + get_validation_actions()

    inlines = [
        AssetAttachmentInline,
        AssetLinkInline,
    ]


class ExchangeAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'url',
    )
    search_fields = (
        'name',
        'slug',
    )


class TradingPairAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'base_asset_obj',
        'quote_asset_obj',
        'exchange_obj',
        'symbol',
    )
    list_select_related = (
        'base_asset_obj',
        'quote_asset_obj',
        'exchange_obj',
    )
    list_filter = (
        'exchange_obj',
    )
    search_fields = (
        'symbol',
    )


admin.site.register(Platform, PlatformAdmin)
admin.site.register(AssetLink, AssetLinkAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(TradingPair, TradingPairAdmin)
