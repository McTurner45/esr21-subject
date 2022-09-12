from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_constants.constants import NO, FEMALE, OMANG, POS, NEG, YES
from edc_facility.import_holidays import import_holidays
from edc_metadata import NOT_REQUIRED, REQUIRED
from edc_metadata.models import CrfMetadata
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_schedule.models import SubjectScheduleHistory
from model_mommy import mommy

from esr21_subject.helper_classes import EnrollmentHelper
from esr21_subject_validation.constants import FIRST_DOSE


@tag('preg')
class TestPregOutcome(TestCase):

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

        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier,
            schedule_name='esr21_fu_schedule3')
        history_obj.offschedule_datetime = get_utcnow() + relativedelta(days=71)
        history_obj.save_base(raw=True)

        self.subject_visit = mommy.make_recipe(
            'esr21_subject.subjectvisit',
            appointment=Appointment.objects.get(
                visit_code='1000',
                subject_identifier=self.subject_identifier),
            report_datetime=get_utcnow(),
            reason=SCHEDULED)

    def test_preg_outcome_not_required_without_pos_test(self):
        mommy.make_recipe(
            'esr21_subject.pregnancytest',
            subject_visit=self.subject_visit,
            preg_performed=YES,
            preg_date=get_utcnow(),
            result=NEG)

        self.subject_visit.save()

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregoutcome',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, NOT_REQUIRED)

    def test_preg_outcome_not_required_without_vac(self):
        mommy.make_recipe(
            'esr21_subject.pregnancytest',
            subject_visit=self.subject_visit,
            preg_performed=YES,
            preg_date=get_utcnow(),
            result=POS)

        self.subject_visit.save()

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregoutcome',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, NOT_REQUIRED)

    def test_preg_outcome_required(self):

        mommy.make_recipe(
            'esr21_subject.vaccinationdetails',
            subject_visit=self.subject_visit,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        mommy.make_recipe(
            'esr21_subject.pregnancytest',
            subject_visit=self.subject_visit,
            preg_performed=YES,
            preg_date=get_utcnow(),
            result=POS)
        mommy.make_recipe(
            'esr21_subject.subjectvisit',
            appointment=Appointment.objects.get(
                visit_code='1028',
                subject_identifier=self.subject_identifier),
            report_datetime=get_utcnow(),
            reason=SCHEDULED)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregoutcome',
                subject_identifier=self.subject_identifier,
                visit_code='1028',
                visit_code_sequence='0').entry_status, REQUIRED)
