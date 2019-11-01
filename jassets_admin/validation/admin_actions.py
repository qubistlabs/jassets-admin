from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..log_tools import ExceptionSpeaker, LogWrapper

from .enums import (
    VALIDATION_METHOD_ACTION_NAME,
    ASSET_LINK_SOURCE_TO_METHOD,
    AssetLinkSource)
from .forms import CollectLinksForm
from .manager import ValidationManager


class ValidationAction:
    def __init__(self, validation_method):
        self.validation_method = validation_method
        self.__name__ = validation_method.value

    def __call__(self, modeladmin, request, queryset):
        manager = ValidationManager()
        manager.set_speaker(ExceptionSpeaker)
        for asset in queryset:
            with LogWrapper(request):
                manager.validate(self.validation_method, asset)


def get_validation_actions():
    result = []
    for method, name in VALIDATION_METHOD_ACTION_NAME.items():
        action_cls = type(
            method.value,
            (ValidationAction, ),
            {'short_description': name},
        )
        action = action_cls(method)
        result.append(action)
    return result


def collect_links(modeladmin, request, queryset):
    """
    Action that launch collecting asset pages links
    Contains intermediate setup form
    """
    form = None
    if 'apply' in request.POST:
        form = CollectLinksForm(request.POST)
        if form.is_valid():
            manager = ValidationManager()
            manager.set_speaker(ExceptionSpeaker)
            for asset in queryset:
                with LogWrapper(request):
                    method = ASSET_LINK_SOURCE_TO_METHOD[
                        AssetLinkSource(form.cleaned_data['source'])
                    ]
                    manager.validate(method, asset, *form.cleaned_data['asset_link_types'])
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = CollectLinksForm(
            initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render(
        request,
        'collect_links.html',
        {'items': queryset, 'form': form, 'title': 'Action settings'},
    )
