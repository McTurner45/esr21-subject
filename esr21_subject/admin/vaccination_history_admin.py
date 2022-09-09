from django.contrib import admin
from edc_model_admin.model_admin_audit_fields_mixin import audit_fieldset_tuple

from .modeladmin_mixins import ModelAdminMixin
from ..admin_site import esr21_subject_admin
from ..forms import VaccinationHistoryForm
from ..models import VaccinationHistory


@admin.register(VaccinationHistory, site=esr21_subject_admin)
class VaccinationHistoryAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = VaccinationHistoryForm

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'report_datetime',
                'received_vaccine',
                'dose_quantity',
                'dose1_product_name',
                'dose1_product_other',
                'dose1_date',
                'dose2_product_name',
                'dose2_product_other',
                'dose2_date',
                'dose3_product_name',
                'dose3_product_other',
                'dose3_date',
                'source_of_info'
            )}),
        audit_fieldset_tuple)

    search_fields = ['subject_identifier']

    list_display = ('subject_identifier', 'report_datetime', )

    radio_fields = {
        'received_vaccine': admin.VERTICAL,
        'dose_quantity': admin.VERTICAL,
        'dose1_product_name': admin.VERTICAL,
        'dose2_product_name': admin.VERTICAL,
        'dose3_product_name': admin.VERTICAL,
        'source_of_info': admin.VERTICAL
    }
