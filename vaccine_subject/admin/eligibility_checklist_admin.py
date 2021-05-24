from django.contrib import admin

from edc_model_admin import ModelAdminBasicMixin
from edc_model_admin.model_admin_audit_fields_mixin import audit_fieldset_tuple
from simple_history.admin import SimpleHistoryAdmin

from ..forms import EligibilityCheckListForm
from ..models import EligibilityCheckList
from ..admin_site import vaccine_subject_admin


@admin.register(EligibilityCheckList, site=vaccine_subject_admin)
class EligibilityCheckListAdmin(ModelAdminBasicMixin,
                                SimpleHistoryAdmin,
                                admin.ModelAdmin):
    form = EligibilityCheckListForm
    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'report_datetime',
                'age_in_years',)}),
        audit_fieldset_tuple)
