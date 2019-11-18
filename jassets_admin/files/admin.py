from django.contrib.admin import TabularInline

from ..models import AssetAttachment

from .forms import AssetAttachmentForm


class AssetAttachmentInline(TabularInline):

    model = AssetAttachment
    form = AssetAttachmentForm
    extra = 1
