from datetime import datetime

from dateutil.tz import gettz
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = 'esr21_subject'
    verbose_name = 'ESR21 Subject CRFs'
    admin_site_name = 'esr21_subject_admin'

    form_versions = {
        'edc_appointment.appointment': 3.0,
        'esr21_subject.adverseevent': 3.0,
        'esr21_subject.concomitantmedication': 3.0,
        'esr21_subject.covid19preventativebehaviours': 3.0,
        'esr21_subject.covid19symptomaticinfections': 3.0,
        'esr21_subject.demographicsdata': 3.0,
        'esr21_subject.eligibilityconfirmation': 3.0,
        'esr21_subject.hospitalisation': 3.0,
        'esr21_subject.informedconsent': 3.0,
        'esr21_subject.medicaldiagnosis': 3.0,
        'esr21_subject.medicalhistory': 3.0,
        'esr21_subject.personalcontactinfo': 3.0,
        'esr21_subject.physicalexam': 3.0,
        'esr21_subject.pregnancystatus': 3.0,
        'esr21_subject.pregnancytest': 3.0,
        'esr21_subject.rapidhivtesting': 3.0,
        'esr21_subject.samplecollection': 3.0,
        'esr21_subject.seriousadverseevent': 3.0,
        'esr21_subject.specialinterestadverseevent': 3.0,
        'esr21_subject.subjectrequisition': 3.0,
        'esr21_subject.subjectvisit': 3.0,
        'esr21_subject.targetedphysicalexamination': 3.0,
        'esr21_subject.vaccinationdetails': 3.0,
        'esr21_subject.vitalsigns': 3.0,
        'esr21_subject.screeningeligibility': 3.0,
        'esr21_subject.vaccinationhistory': 3.0,
        'esr21_subject.covid19results': 3.0,
        'esr21_subject.pregoutcome': 3.0
        }


if settings.APP_NAME == 'esr21_subject':
    from edc_appointment.appointment_config import AppointmentConfig
    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
    from edc_appointment.constants import COMPLETE_APPT
    from edc_constants.constants import FAILED_ELIGIBILITY
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_meddra.apps import AppConfig as BaseEdcMeddraAppConfig
    from edc_metadata.apps import AppConfig as BaseEdcMetadataAppConfig
    from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfigs
    from edc_timepoint.apps import AppConfig as BaseEdcTimepointAppConfig
    from edc_timepoint.timepoint import Timepoint
    from edc_timepoint.timepoint_collection import TimepointCollection
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig
    from edc_visit_tracking.constants import MISSED_VISIT, COMPLETED_PROTOCOL_VISIT
    from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, LOST_VISIT
    from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        country = 'botswana'
        definitions = {
            '7-day clinic': dict(days=[MO, TU, WE, TH, FR, SA, SU],
                                 slots=[100, 100, 100, 100, 100, 100, 100]),
            '5-day clinic': dict(days=[MO, TU, WE, TH, FR],
                                 slots=[100, 100, 100, 100, 100])}

    class EdcProtocolAppConfig(BaseEdcProtocolAppConfigs):
        protocol = 'AZD1222'
        protocol_name = 'AZD 1222 - ESR-21-21311'
        protocol_number = '150'
        protocol_title = ''
        study_open_datetime = datetime(
            2021, 4, 15, 0, 0, 0, tzinfo=gettz('UTC'))
        study_close_datetime = datetime(
            2025, 12, 1, 0, 0, 0, tzinfo=gettz('UTC'))

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
        configurations = [
            AppointmentConfig(
                model='edc_appointment.appointment',
                related_visit_model='esr21_subject.subjectvisit',
                appt_type='clinic'), ]

    class EdcTimepointAppConfig(BaseEdcTimepointAppConfig):
        timepoints = TimepointCollection(
            timepoints=[
                Timepoint(
                    model='edc_appointment.appointment',
                    datetime_field='appt_datetime',
                    status_field='appt_status',
                    closed_status=COMPLETE_APPT),
                Timepoint(
                    model='edc_appointment.historicalappointment',
                    datetime_field='appt_datetime',
                    status_field='appt_status',
                    closed_status=COMPLETE_APPT), ])

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        report_datetime_allowance = -1
        visit_models = {
            'esr21_subject': ('subject_visit', 'esr21_subject.subjectvisit'), }

    class EdcMetadataAppConfig(BaseEdcMetadataAppConfig):

        reason_field = {'esr21_subject.subjectvisit': 'reason'}
        create_on_reasons = [SCHEDULED, UNSCHEDULED, COMPLETED_PROTOCOL_VISIT]
        delete_on_reasons = [LOST_VISIT, MISSED_VISIT, FAILED_ELIGIBILITY]

    class EdcMeddraAppConfig(BaseEdcMeddraAppConfig):
        version = 24.1
        ctcae_version = 5.0
