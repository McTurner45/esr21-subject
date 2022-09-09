from django import forms
from edc_form_validators import FormValidatorMixin
from esr21_subject_validation.form_validators import SubjectRequisitionFormValidator
from edc_lab.forms.modelform_mixins import RequisitionFormMixin

from ..models import SubjectRequisition


class SubjectRequisitionForm(RequisitionFormMixin,
                             FormValidatorMixin):

    form_validator_cls = SubjectRequisitionFormValidator

    requisition_identifier = forms.CharField(
        label='Requisition identifier',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    def clean(self):
        super().clean()

    class Meta:
        model = SubjectRequisition
        fields = '__all__'
