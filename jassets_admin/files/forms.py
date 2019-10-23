from uuid import uuid4
from django import forms
from django.forms.utils import ErrorList

from .helpers import save_attachment, get_attachment, get_file_hash


READONLY_FIELDS = ('id', 'version', 'path')


class AssetAttachmentForm(forms.ModelForm):
    attachment = forms.FileField(label='Local file', required=False)

    # FIXME does'n work this way for some reason
    field_order = ('name', 'path', 'attachment', 'metadata', 'id', 'version')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None, use_required_attribute=None,
                 renderer=None):
        initial = initial or {}
        if instance is not None:
            initial['attachment'] = get_attachment(instance)
        super().__init__(
            data=data, files=files, auto_id=auto_id, prefix=prefix,
            initial=initial, error_class=error_class, label_suffix=label_suffix,
            empty_permitted=empty_permitted, instance=instance,
            use_required_attribute=use_required_attribute, renderer=renderer
        )
        self._setup_fields()

    def clean_attachment(self):
        data = self.cleaned_data.get('attachment')
        if self.changed_data and not data:
            raise forms.ValidationError('Field is required to fill')
        return data

    def save(self, commit=True):
        if 'attachment' in self.changed_data:
            local_path, remote_path = save_attachment(self.cleaned_data.get('attachment', None))
            self.instance.path = remote_path
            self.instance.version = get_file_hash(local_path)
        if not self.instance.id:
            self.instance.id = uuid4()
        return super().save(commit)

    def _setup_fields(self):
        for name, field in self.fields.items():
            if name in READONLY_FIELDS:
                field.required = False
                field.widget.attrs['readonly'] = True
