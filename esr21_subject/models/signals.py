from django.apps import apps as django_apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_appointment.constants import COMPLETE_APPT
from edc_appointment.models.appointment import Appointment
from edc_base.utils import get_uuid
from edc_constants.constants import YES
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_registration.models import RegisteredSubject
from .eligibility_confirmation import EligibilityConfirmation
from .adverse_event import AdverseEventRecord
from .informed_consent import InformedConsent
from .onschedule import OnSchedule
from .vaccination_details import VaccinationDetails
from .vaccination_history import VaccinationHistory


@receiver(post_save, weak=False, sender=AdverseEventRecord,
          dispatch_uid="metadata_update_on_post_save")
def metadata_update_on_post_save(sender, instance, raw, created, using,
                                 update_fields, **kwargs):
    """Update the meta data record on post save of a CRF model.
    """

    if not raw:
        try:
            instance.adverse_event.reference_updater_cls(model_obj=instance.adverse_event)
        except AttributeError:
            pass

        try:
            instance.adverse_event.metadata_update()
        except AttributeError as e:
            if 'metadata_update' not in str(e):
                raise
        else:
            if django_apps.get_app_config('edc_metadata_rules').metadata_rules_enabled:
                instance.adverse_event.run_metadata_rules_for_crf()


@receiver(post_save, weak=False, sender=Appointment,
          dispatch_uid='appointment_on_post_save')
def appointment_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        if (
                instance.visit_code == '2028' and instance.schedule_name == 'esr21_illness_schedule'
                and instance.appt_status == COMPLETE_APPT):

            _, schedule = site_visit_schedules.get_by_onschedule_model_schedule_name(
                onschedule_model='esr21_subject.onscheduleill',
                name=instance.schedule_name)

            schedule.take_off_schedule(subject_identifier=instance.subject_identifier)

            try:
                latest_offschedule = schedule.offschedule_model_cls.objects.get(
                    subject_identifier=instance.subject_identifier,
                    schedule_name__isnull=True)
            except schedule.offschedule_model_cls.DoesNotExist:
                pass
            else:
                latest_offschedule.schedule_name = instance.schedule_name
                latest_offschedule.save()


def put_on_schedule(schedule_name, onschedule_model, instance=None,
                    onschedule_datetime=None):
    if instance:
        _, schedule = site_visit_schedules.get_by_onschedule_model_schedule_name(
            onschedule_model=onschedule_model, name=schedule_name)

        schedule.put_on_schedule(
            subject_identifier=instance.subject_identifier,
            onschedule_datetime=onschedule_datetime,
            schedule_name=schedule_name)


def refresh_schedule(schedule_name, onschedule_model, instance=None):
    if instance:
        _, schedule = site_visit_schedules.get_by_onschedule_model_schedule_name(
            onschedule_model=onschedule_model,
            name=schedule_name)
        schedule.refresh_schedule(
            subject_identifier=instance.subject_identifier)


def is_subcohort_full():
    onschedule_subcohort = OnSchedule.objects.filter(
        schedule_name='esr21_sub_enrol_schedule')

    return onschedule_subcohort.count() == 3000


@receiver(post_save, weak=False, sender=InformedConsent,
          dispatch_uid="informed_consent_on_post_save")
def informed_consent_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw and created:
        subject_identifier = instance.subject_identifier
        identity = instance.identity
        try:
            screening_eligibility = EligibilityConfirmation.objects.get(
                screening_identifier=instance.screening_identifier)
        except EligibilityConfirmation.DoesNotExist:
            pass
        else:
            screening_eligibility.subject_identifier = subject_identifier
            screening_eligibility.save_base(raw=True)
        try:
            consent = InformedConsent.objects.filter(identity=identity).exclude(
                subject_identifier=subject_identifier).latest('-created')
        except InformedConsent.DoesNotExist:
            pass
        else:
            if consent.screened_out:
                consent.is_duplicate = True
                consent.save()
                try:
                    registered_subject = RegisteredSubject.objects.get(
                        identity=consent.identity)
                except RegisteredSubject.DoesNotExist:
                    pass
                else:
                    registered_subject.identity = None
                    registered_subject.identity_or_pk = get_uuid()
                    registered_subject.save()


@receiver(post_save, weak=False, sender=VaccinationDetails,
          dispatch_uid='vaccination_details_on_post_save')
def vaccination_details_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        subject_identifier = instance.subject_visit.subject_identifier
        try:
            consent = InformedConsent.objects.filter(
                subject_identifier=subject_identifier).latest(
                    'consent_datetime')
        except InformedConsent.DoesNotExist:
            raise Exception('Informed consent for participant does not exist.')
        else:
            if consent.version == '3':
                dose = selected_dose(vacc_detail=instance)
                VaccinationHistory.objects.update_or_create(
                    subject_identifier=subject_identifier,
                    defaults={'received_vaccine': YES,
                              'dose_quantity': dose,
                              f'dose{dose}_product_name': 'azd_1222',
                              f'dose{dose}_date': instance.vaccination_date.date()})


def selected_dose(vacc_detail=None):
    dose_map = {'first_dose': '1',
                'second_dose': '2',
                'booster_dose': '3'}
    return dose_map.get(getattr(vacc_detail, 'received_dose_before'))
