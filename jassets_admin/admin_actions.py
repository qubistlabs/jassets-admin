from django.contrib import messages

from .exceptions import ShowWarning, ShowMessage, ShowError
from .log_tools import ExceptionSpeaker
from .validation.enums import ValidationMethodEnum, VALIDATION_METHOD_VERBOSE_NAMES
from .validation.manager import ValidationManager


class ValidationAction:
    def __init__(self, validation_method):
        self.validation_method = validation_method
        self.__name__ = validation_method.value

    def __call__(self, modeladmin, request, queryset):
        manager = ValidationManager()
        manager.set_speaker(ExceptionSpeaker)
        for asset in queryset:
            try:
                manager.validate(self.validation_method, asset)
            except ShowWarning as warning:
                messages.warning(request, warning)
            except ShowMessage as message:
                messages.info(request, message)
            except ShowError as message:
                messages.error(request, message)


def get_validation_actions():
    result = []
    for v in ValidationMethodEnum:
        text = f'Validate {VALIDATION_METHOD_VERBOSE_NAMES[v]}'
        action_cls = type(
            v.value,
            (ValidationAction, ),
            {'short_description': text},
        )
        action = action_cls(v)
        result.append(action)
    return result
