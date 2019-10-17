from django.forms import ModelForm, BaseInlineFormSet

from .query import StaticDataModel


class StaticDataForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_unique(self):
        pass

    def save(self, commit=True):
        return self.instance


class StaticDataInlineFormSet(BaseInlineFormSet):

    model: StaticDataModel

    def save(self, commit=True):
        instances = super().save(commit)
        self.model.save_data(*instances)
        return instances
