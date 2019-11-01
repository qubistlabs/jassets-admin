from django import forms

from ..enums import AssetLinkType

from .enums import AssetLinkSource


class CollectLinksForm(forms.Form):
    """ Action setup form """
    _selected_action = forms.CharField(
        widget=forms.MultipleHiddenInput
    )
    asset_link_types = forms.MultipleChoiceField(
        choices=AssetLinkType.choices(),
        label='Type of link'
    )
    source = forms.ChoiceField(
        choices=AssetLinkSource.choices(),
        label='Source'
    )
