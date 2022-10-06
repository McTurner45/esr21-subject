from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO, FEMALE, OMANG
from edc_facility.import_holidays import import_holidays
from edc_metadata.constants import REQUIRED, NOT_REQUIRED
from edc_metadata.models import CrfMetadata
from model_mommy import mommy

from esr21_subject.helper_classes import EnrollmentHelper
from ..models import OnSchedule


@tag('booster')
class TestBoosterScheduleSetup(TestCase):
    databases = '__all__'

    def setUp(self):
        import_holidays()

        self.enrol_helper = EnrollmentHelper

        self.eligibility = mommy.make_recipe(
            'esr21_subject.eligibilityconfirmation', )

        self.consent_options = {
            'screening_identifier': self.eligibility.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 3,
            'dob': (get_utcnow() - relativedelta(years=45)).date(),
            'first_name': 'TEST ONE',
            'last_name': 'TEST',
            'initials': 'TOT',
            'identity': '123425678',
            'confirm_identity': '123425678',
            'identity_type': OMANG,
            'gender': FEMALE}

        self.consent = mommy.make_recipe(
            'esr21_subject.informedconsent',
            **self.consent_options)

        mommy.make_recipe(
            'esr21_subject.screeningeligibility',
            subject_identifier=self.consent.subject_identifier,
            is_eligible=True)

        self.subject_identifier = self.consent.subject_identifier

        mommy.make_recipe(
            'esr21_subject.vaccinationhistory',
            subject_identifier=self.consent.subject_identifier,
            received_vaccine=YES,
            dose_quantity='2', )

        self.cohort = 'esr21'
        self.schedule_enrollment = self.enrol_helper(
            cohort=self.cohort, subject_identifier=self.subject_identifier)
        self.schedule_enrollment.schedule_enrol()

    def test_booster_dose_onschedule(self):
        self.assertEqual(OnSchedule.objects.filter(
            subject_identifier=self.consent.subject_identifier,
            schedule_name='esr21_boost_schedule').count(), 1)

    def test_booster_dose_not_onschedule(self):
        consent = mommy.make_recipe(
            'esr21_subject.informedconsent',
            subject_identifier='123-9872')

        mommy.make_recipe(
            'esr21_subject.screeningeligibility',
            subject_identifier=consent.subject_identifier,
            is_eligible=True)

        mommy.make_recipe(
            'esr21_subject.vaccinationhistory',
            subject_identifier=consent.subject_identifier,
            received_vaccine=NO,
            dose_quantity=None)

        self.assertEqual(OnSchedule.objects.filter(
            subject_identifier=consent.subject_identifier,
            schedule_name='esr21_booster_schedule').count(), 0)

        consent = mommy.make_recipe(
            'esr21_subject.informedconsent',
            subject_identifier='123-9871')

        mommy.make_recipe(
            'esr21_subject.screeningeligibility',
            subject_identifier=consent.subject_identifier,
            is_eligible=True)

        mommy.make_recipe(
            'esr21_subject.vaccinationhistory',
            subject_identifier=consent.subject_identifier,
            received_vaccine=YES,
            dose_quantity=1)

        self.assertEqual(OnSchedule.objects.filter(
            subject_identifier=consent.subject_identifier,
            schedule_name='esr21_booster_schedule').count(), 0)

    def test_booster_appointments_created(self):
        """Assert that four appointments were created"""

        self.assertEqual(Appointment.objects.filter(
            subject_identifier=self.consent.subject_identifier).count(), 4)

    @tag('cccx')
    def test_metadata_creation_booster(self):
        appointment_170 = Appointment.objects.get(
            subject_identifier=self.consent.subject_identifier,
            visit_code='1170')

        mommy.make_recipe(
            'esr21_subject.subjectvisit',
            subject_identifier=self.consent.subject_identifier,
            report_datetime=get_utcnow(),
            appointment=appointment_170)

        entry_required = ['vaccinationdetails', 'physicalexam', 'vitalsigns',
                          'pregnancystatus', 'demographicsdata', 'rapidhivtesting',
                          'covid19preventativebehaviours', 'medicalhistory']

        for required in entry_required:
            print(CrfMetadata.objects.get(
                model=f'esr21_subject.{required}',
                subject_identifier=self.consent.subject_identifier,
                visit_code='1170').entry_status)
            self.assertEqual(
                CrfMetadata.objects.get(
                    model=f'esr21_subject.{required}',
                    subject_identifier=self.consent.subject_identifier,
                    visit_code='1170').entry_status, REQUIRED)

    @tag('cca')
    def test_metadata_not_req_booster(self):
        appointment_170 = Appointment.objects.get(
            subject_identifier=self.consent.subject_identifier,
            visit_code='1170')

        appointment_1198 = Appointment.objects.get(
            subject_identifier=self.consent.subject_identifier,
            visit_code='1198')

        mommy.make_recipe(
            'esr21_subject.subjectvisit',
            subject_identifier=self.consent.subject_identifier,
            report_datetime=get_utcnow(),
            visit_code_sequence=1,
            appointment=appointment_170)

        mommy.make_recipe(
            'esr21_subject.subjectvisit',
            subject_identifier=self.consent.subject_identifier,
            report_datetime=get_utcnow(),
            appointment=appointment_1198)

        entry_required = ['demographicsdata', 'rapidhivtesting',
                          'covid19preventativebehaviours', 'medicalhistory']

        for required in entry_required:
            self.assertEqual(
                CrfMetadata.objects.get(
                    model=f'esr21_subject.{required}',
                    subject_identifier=self.consent.subject_identifier,
                    visit_code='1198').entry_status, NOT_REQUIRED)
