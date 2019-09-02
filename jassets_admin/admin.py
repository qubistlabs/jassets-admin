from django.contrib import admin

from .models import TradingPair, Platform, Asset, Exchange


class BaseModelAdmin(admin.ModelAdmin):
    list_per_page = 25


class PlatformAdmin(BaseModelAdmin):
    list_display = ('id', 'name', 'symbol', 'main_asset_obj')
    list_select_related = ('main_asset_obj', )
    search_fields = ('name', 'symbol')
    list_filter = ('main_asset_obj__type', 'main_asset_obj__is_active')


class AssetAdmin(BaseModelAdmin):
    list_display = ('id', 'uuid', 'name', 'description', 'platform_obj', 
                    'symbol', 'type', 'is_active', 'address', 'properties', 
                    'created', 'updated')
    list_select_related = ('platform_obj', )
    search_fields = ('name', 'symbol')
    list_filter = ('platform_obj', 'type', 'is_active', 'created', 'updated')


class ExchangeAdmin(BaseModelAdmin):
    list_display = ('id', 'name', 'slug', 'url')
    search_fields = ('name', 'slug')


class TradingPairAdmin(BaseModelAdmin):
    list_display = ('id', 'base_asset_obj', 'quote_asset_obj', 'exchange_obj',
                    'symbol')
    list_select_related = ('base_asset_obj', 'quote_asset_obj', 'exchange_obj')


admin.site.register(Platform, PlatformAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(TradingPair, TradingPairAdmin)
