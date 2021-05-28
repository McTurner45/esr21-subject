from django.contrib import admin

from edc_model_admin import ModelAdminBasicMixin
from edc_model_admin.model_admin_audit_fields_mixin import audit_fieldset_tuple
from simple_history.admin import SimpleHistoryAdmin

from ..forms import VaccinationDetailsForm
from ..models import VaccinationDetails
from ..admin_site import esr21_subject_admin


@admin.register(VaccinationDetails, site=esr21_subject_admin)
class VaccinationDetailsAdmin(ModelAdminBasicMixin,
                              SimpleHistoryAdmin,
                              admin.ModelAdmin):

    form = VaccinationDetailsForm

    fieldsets = (
        (None, {
            'fields': (
                'report_datetime',
                'vaccination_place',
                'vaccination_dt',
                'route',
                'location',
                'location_other',
                'admin_per_protocol',
                'reason_not_per_protocol',
                'dose_administered',
                'batch_number',
                'expiry_date',
                'provider_name',
                'next_vaccination',
            ),
        }),
        audit_fieldset_tuple)
