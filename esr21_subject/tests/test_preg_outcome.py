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

    def test_preg_outcome_required(self):
        self.assertEqual(Appointment.objects.filter(
            subject_identifier=self.subject_identifier,
            schedule_name='esr21_enrol_schedule3').count(), 2)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregnancystatus',
                subject_identifier=self.subject_identifier,
                visit_code='1000',
                visit_code_sequence='0').entry_status, REQUIRED)

        mommy.make_recipe(
            'esr21_subject.pregnancytest',
            subject_visit=self.subject_visit,
            preg_performed=YES,
            preg_date=get_utcnow(),
            result=POS)

        day_28_follow = mommy.make_recipe(
            'esr21_subject.subjectvisit',
            appointment=Appointment.objects.get(
                visit_code='1028',
                subject_identifier=self.subject_identifier),
            report_datetime=get_utcnow(),
            reason=SCHEDULED)

        mommy.make_recipe(
            'esr21_subject.pregnancytest',
            subject_visit=day_28_follow,
            preg_performed=YES,
            preg_date=get_utcnow(),
            result=NEG)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregoutcome',
                subject_identifier=self.subject_identifier,
                visit_code='1028',
                visit_code_sequence='0').entry_status, REQUIRED)

        mommy.make_recipe(
            'esr21_subject.pregoutcome',
            report_datetime=get_utcnow(),
            subject_visit=day_28_follow,)

        day_70_visit = mommy.make_recipe(
            'esr21_subject.subjectvisit',
            appointment=Appointment.objects.get(
                visit_code='1070',
                subject_identifier=self.subject_identifier),
            report_datetime=get_utcnow() + relativedelta(days=2),
            reason=SCHEDULED)

        mommy.make_recipe(
            'esr21_subject.pregnancytest',
            subject_visit=day_70_visit,
            preg_date=get_utcnow() + relativedelta(days=2),
            result=NEG)

        self.assertEqual(
            CrfMetadata.objects.get(
                model='esr21_subject.pregoutcome',
                subject_identifier=self.subject_identifier,
                visit_code='1070',
                visit_code_sequence='0').entry_status, NOT_REQUIRED)
