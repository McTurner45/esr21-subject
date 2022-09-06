from django.contrib import admin
from edc_model_admin.model_admin_audit_fields_mixin import audit_fieldset_tuple

from .modeladmin_mixins import ModelAdminMixin
from ..admin_site import esr21_subject_admin
from ..models import ScreenOut
from ..forms import ScreenOutForm

@admin.register(ScreenOut, site=esr21_subject_admin)
class ScreenOutAdmin(ModelAdminMixin, admin.ModelAdmin):
    
    form = ScreenOutForm
    
    fieldsets = (
        (None, {
            "fields": (
                'subject_identifier',
                'report_datetime',
                'screen_out_reason',
                'screen_out_other',
                'comment',
            ),
        }),audit_fieldset_tuple
    )
    
    search_fields = ['subject_identifier']

    list_display = ('subject_identifier', 'report_datetime', )

    radio_fields = {
        'screen_out_reason': admin.VERTICAL,
    }
    
