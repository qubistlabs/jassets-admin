from django.contrib import admin

from jassets_admin.validation.adapters import ADAPTER_MAP
from jassets_admin.validation.admin_actions import apply_changes, discard_changes
from jassets_admin.validation.enums import VALIDATION_METHOD_ACTION_NAME, ValidationMethodEnum
from jassets_admin.validation.models import AssetHistory, ValidationQueue


class TaskNameFilter(admin.SimpleListFilter):
    title = 'Task name'
    parameter_name = 'task_name'

    def lookups(self, request, model_admin):
        return ((k.value, v) for k, v in VALIDATION_METHOD_ACTION_NAME.items())

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            queryset = queryset.filter(validation_method=value)
        return queryset


class AssetHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'uuid',
        'name',
        'symbol',
        'type',
        'is_active',
        'properties',
        'state',
        'task_name',
        'result',
        'validation_time',
    )
    search_fields = (
        'name',
        'symbol',
    )
    list_filter = (
        'state',
        TaskNameFilter,
        'validation_time',
        'type',
        'is_active',
    )
    list_per_page = 25

    actions = (apply_changes, discard_changes)

    def task_name(self, obj):
        if obj.validation_method:
            return VALIDATION_METHOD_ACTION_NAME.get(ValidationMethodEnum(obj.validation_method))

    def result(self, obj):
        if obj.validation_method:
            adapter_cls = ADAPTER_MAP[ValidationMethodEnum(obj.validation_method)]
            return adapter_cls.get_result_from_validation_results_dict(obj.validation_results_dict)
        else:
            return obj.validation_results_dict


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
