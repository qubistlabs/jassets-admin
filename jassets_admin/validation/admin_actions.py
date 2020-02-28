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
        log_wrapper = LogWrapper(request)
        for asset in queryset:
            with log_wrapper:
                manager.validate(
                    validation_method=self.validation_method,
                    asset=asset,
                    user=request.user,
                )


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
            log_wrapper = LogWrapper(request)
            for asset in queryset:
                with log_wrapper:
                    method = ASSET_LINK_SOURCE_TO_METHOD[
                        AssetLinkSource(form.cleaned_data['source'])
                    ]
                    manager.validate(
                        validation_method=method,
                        asset=asset,
                        user=request.user,
                        *form.cleaned_data['asset_link_types'],
                    )
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = CollectLinksForm(
            initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render(
        request,
        'collect_links.html',
        {'items': queryset, 'form': form, 'title': 'Action settings'},
    )


def approve_or_discard(modeladmin, request, queryset, is_approved):
    manager = ValidationManager()
    manager.set_speaker(ExceptionSpeaker)
    log_wrapper = LogWrapper(request)
    for history_entry in queryset:
        with log_wrapper:
            manager.approval(history_entry, is_approved)


def apply_changes(modeladmin, request, queryset):
    approve_or_discard(modeladmin, request, queryset, True)


def discard_changes(modeladmin, request, queryset):
    approve_or_discard(modeladmin, request, queryset, False)
