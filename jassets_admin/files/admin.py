from django.contrib.admin import TabularInline

from .forms import StaticDataForm, StaticDataInlineFormSet
from .models import AssetAttachment


class AssetAttachmentInline(TabularInline):

    model = AssetAttachment
    form = StaticDataForm
    formset = StaticDataInlineFormSet
    extra = 1
