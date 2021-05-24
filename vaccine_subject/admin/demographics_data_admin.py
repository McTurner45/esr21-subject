from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..forms import DemographicsDataForm
from ..models import DemographicsData
from ..admin_site import vaccine_subject_admin


@admin.register(DemographicsData, site=vaccine_subject_admin)
class DemographicDataAdmin(admin.ModelAdmin):
    form = DemographicsDataForm

    list_display = ('marital_status',
                    'ethnicity',
                    'highest_education',
                    'own_phone')
    list_filter = ('marital_status',
                   'ethnicity',
                   'highest_education',
                   'own_phone')

    fieldsets = (
        (None, {
            'fields': [
                'report_datetime',
                'marital_status',
                'marital_status_other',
                'ethnicity',
                'ethnicity_other',
                'highest_education',
                'current_occupation',
                'current_occupation_other',
                'provides_money',
                'provides_money_other',
                'money_earned',
                'money_earned_other',
                'own_phone',
                'water_source',
                'house_electrified',
                'toilet_facility',
                'toilet_facility_other',
                'house_people_number',
                'house_type']}
         ), audit_fieldset_tuple)

    radio_fields = {'marital_status': admin.VERTICAL,
                    'ethnicity': admin.VERTICAL,
                    'highest_education': admin.VERTICAL,
                    'current_occupation': admin.VERTICAL,
                    'provides_money': admin.VERTICAL,
                    'money_earned': admin.VERTICAL,
                    'own_phone': admin.VERTICAL,
                    'water_source': admin.VERTICAL,
                    'house_electrified': admin.VERTICAL,
                    'toilet_facility': admin.VERTICAL,
                    'house_type': admin.VERTICAL, }
