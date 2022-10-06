from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base.utils import get_utcnow
from edc_constants.constants import OMANG, FEMALE, MALE, NO, YES, NEG, POS
from edc_facility.import_holidays import import_holidays
from edc_metadata.constants import REQUIRED, NOT_REQUIRED
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from model_mommy import mommy

from ..models import ScreeningEligibility, Covid19Results
from ..helper_classes import EnrollmentHelper


class TestRuleGroups(TestCase):

    def setUp(self):
        import_holidays()

        self.enrol_helper = EnrollmentHelper

        self.eligibility = mommy.make_recipe(
            'esr21_subject.eligibilityconfirmation', )

        self.consent_options = {
            'screening_identifier': self.eligibility.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 1,
            'dob': (get_utcnow() - relativedelta(years=45)).date(),
            'first_name': 'TEST ONE',
            'last_name': 'TEST',
            'initials': 'TOT',
            'identity': '123425678',
            'confirm_identity': '123425678',
            'identity_type': OMANG,
            'gender': FEMALE}

        consent = mommy.make_recipe(
            'esr21_subject.informedconsent',
            **self.consent_options)

        mommy.make_recipe(
            'esr21_subject.screeningeligibility',
            subject_identifier=consent.subject_identifier,
            symptomatic_infections_experiences=NO,
            is_eligible=True)

        self.subject_identifier = consent.subject_identifier

        mommy.make_recipe(
            'esr21_subject.vaccinationhistory',
            subject_identifier=self.subject_identifier,
            received_vaccine=NO,
            dose_quantity=None)

        self.cohort = 'esr21'
        self.schedule_enrollment = self.enrol_helper(
            cohort=self.cohort, subject_identifier=self.subject_identifier)
        self.schedule_enrollment.schedule_enrol()

        self.subject_visit = mommy.make_recipe(
            'esr21_subject.subjectvisit',
            appointment=Appointment.objects.get(
                visit_code='1000',
                visit_code_sequence='0',
                subject_identifier=consent.subject_identifier),
            report_datetime=get_utcnow(),
            reason=SCHEDULED)

    def test_pregnancy_form_required(self):
        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregnancystatus',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, REQUIRED)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregnancytest',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, NOT_REQUIRED)

    def test_pregnancy_status_form_not_required(self):

        eligibility = mommy.make_recipe(
            'esr21_subject.eligibilityconfirmation')

        consent_options = {
            'screening_identifier': eligibility.screening_identifier,
            'consent_datetime': get_utcnow(),
            'version': 1,
            'dob': (get_utcnow() - relativedelta(years=45)).date(),
            'first_name': 'JOHN',
            'last_name': 'DOE',
            'initials': 'JD',
            'identity': '123415678',
            'confirm_identity': '123415678',
            'identity_type': OMANG,
            'gender': MALE}

        subject_consent = mommy.make_recipe(
            'esr21_subject.informedconsent',
            **consent_options)

        mommy.make_recipe(
            'esr21_subject.screeningeligibility',
            subject_identifier=subject_consent.subject_identifier,
            is_eligible=True)

        mommy.make_recipe(
            'esr21_subject.vaccinationhistory',
            subject_identifier=subject_consent.subject_identifier,
            received_vaccine=NO,
            dose_quantity=None)

        self.schedule_enrollment = self.enrol_helper(
            cohort=self.cohort, subject_identifier=subject_consent.subject_identifier)
        self.schedule_enrollment.schedule_enrol()

        mommy.make_recipe(
            'esr21_subject.subjectvisit',
            appointment=Appointment.objects.get(
                visit_code='1000',
                subject_identifier=subject_consent.subject_identifier),
            report_datetime=get_utcnow(),
            reason=SCHEDULED)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregnancystatus',
                subject_identifier=subject_consent.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, NOT_REQUIRED)

    def test_pregnancy_test_not_required(self):
        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregnancytest',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, NOT_REQUIRED)

    def test_pregnancy_test_required(self):
        mommy.make_recipe(
            'esr21_subject.pregnancystatus',
            subject_visit=self.subject_visit,
            post_menopausal=NO,
            surgically_sterilized=NO)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregnancytest',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, REQUIRED)

    @tag('rg')
    def test_pos_preg_vax_not_required(self):
        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.vaccinationdetails',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, REQUIRED)

        mommy.make_recipe(
            'esr21_subject.pregnancystatus',
            subject_visit=self.subject_visit,
            post_menopausal=NO,
            surgically_sterilized=NO)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregnancytest',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, REQUIRED)

        mommy.make_recipe(
            'esr21_subject.pregnancytest',
            subject_visit=self.subject_visit,
            result=POS)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.vaccinationdetails',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, NOT_REQUIRED)

    def test_covid19_results(self):
        mommy.make_recipe(
            'esr21_subject.covid19results',
            subject_visit=self.subject_visit,
            covid_result=NEG)

        covid19 = CrfMetadata.objects.filter(
            subject_identifier=self.subject_identifier)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.physicalexam',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, REQUIRED)
