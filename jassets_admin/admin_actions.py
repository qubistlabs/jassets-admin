from .validation.enums import ValidationMethodEnum
from .validation.manager import ValidationManager


class ValidationAction:
    def __init__(self, validation_method):
        self.validation_method = validation_method
        self.__name__ = validation_method.value

    def __call__(self, modeladmin, request, queryset):
        for asset in queryset:
            ValidationManager.validate(self.validation_method, asset)


def get_validation_actions():
    result = []
    for v in ValidationMethodEnum:
        action_cls = type(
            v.value,
            (ValidationAction, ),
            {'short_description': ValidationMethodEnum.get_verbose_name(v)},
        )
        action = action_cls(v)
        result.append(action)
    return result
