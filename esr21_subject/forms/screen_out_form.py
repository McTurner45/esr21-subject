from django import forms
from ..models import ScreenOut

class ScreenOutForm(forms.ModelForm):
    
    # form_validator_cls = ScreenOutFormValidator
    class Meta:
        model = ScreenOut
        fields = '__all__'
