from django.db import models
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators.date import date_not_future
from edc_base.sites import SiteModelMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import NO

from ..choices import SMOKED_STATUS_CHOICES, ALCOHOL_STATUS_CHOICES, MODE_TRANSPORT
from .list_models import Symptoms, Diseases
from .model_mixins import CrfModelMixin


class MedicalHistory(CrfModelMixin):

    pregnancy_status = models.CharField(
        verbose_name=('Are you pregnant or nursing or do you plan to get pregnant in the next '
                      '3 months?'),
        max_length=3,
        choices=YES_NO,
        default=NO,
        null=True,
        blank=True
    )

    # ADDED QUESTIONS FROM THE DOC
    thrombosis_or_thrombocytopenia = models.CharField(
        verbose_name=('Does individuals have any risk factors for or a reported history of '
                      'thrombosis and/or thrombocytopenia?'),
        max_length=3,
        choices=YES_NO,
        default=NO,
    )

    clinical_bleeding = models.CharField(
        verbose_name=('Ever experienced clinically significant bleeding, or prior history '
                      'of significant bleeding or bruising following intramuscular injections '
                      'or venepuncture?'),
        max_length=20,
        choices=YES_NO,
        default=NO,
        help_text=('(eg, factor deficiency, coagulopathy, or '
                   'platelet disorder) '),
    )

    guillain_barre_syndrome = models.CharField(
        verbose_name='Any history of Guillain-Barré syndrome?',
        max_length=3,
        choices=YES_NO,
        default=NO,)

    suspected_immuno_condition = models.CharField(
        verbose_name=('Any confirmed or suspected immunosuppressive or immunodeficient state '
                      '(including Asplenia)?'),
        max_length=3,
        choices=YES_NO,
        default=NO,)

    relevant_history = models.CharField(
        verbose_name='Does the subject have any relevant Medical History?',
        max_length=3,
        choices=YES_NO,)

    prior_covid_infection = models.CharField(
        verbose_name='Has the participant had a prior infection of '
                     'SARS-CoV-2/COVID 19?',
        max_length=3,
        choices=YES_NO,)

    covid_symptoms = models.ManyToManyField(
        Symptoms,
        verbose_name='If yes, did the participant experience any symptoms?',
        blank=True)

    symptoms_other = models.TextField(
        verbose_name='If other specify',
        blank=True,
        null=True)

    smoking_status = models.CharField(
        choices=SMOKED_STATUS_CHOICES,
        verbose_name='Smoking status/history',
        max_length=20,)

    alcohol_status = models.CharField(
        choices=ALCOHOL_STATUS_CHOICES,
        verbose_name='Alcohol Use',
        max_length=50,
    )

    diabetes = models.CharField(
        verbose_name='Has the participant been diagnosed with diabetes mellitus?',
        choices=YES_NO,
        max_length=3
    )

    comorbidities = models.ManyToManyField(Diseases,
                                           verbose_name='Comorbidities')

    comorbidities_other = models.CharField(
        verbose_name='Other specify',
        max_length=50,
        blank=True,
        null=True)

    received_art = models.CharField(
        verbose_name='Has the participant ever taken anti-retroviral therapy '
        'or ART?',
        max_length=3,
        choices=YES_NO,
        blank=True,
        null=True)

    no_of_mass_gathering = models.PositiveIntegerField(
        default=0,
        verbose_name=('How many mass gatherings has the participant attended '
                      'in the preceding 12 weeks? '),
        help_text=('eg, weddings, funerals; defined as 50 or more people')
    )

    no_internal_trips = models.PositiveIntegerField(
        default=0,
        verbose_name=('How many COVID-19 inter-zonal trips has the '
                      'participant made in Botswana in the past 12 weeks? ')
    )

    mode_of_transport = models.CharField(
        choices=MODE_TRANSPORT,
        verbose_name='Mode of Transport',
        max_length=30,
        blank=True
    )

    using_shared_kitchen = models.CharField(
        choices=YES_NO,
        verbose_name='Is the participant using a shared kitchen/dining at '
                     'work?',
        max_length=3
    )

    history = HistoricalRecords()

    class Meta(CrfModelMixin.Meta):
        app_label = 'esr21_subject'
        verbose_name = 'Medical History'
        verbose_name_plural = 'Medical History'


class MedicalDiagnosisManager(models.Manager):

    def get_by_natural_key(self, start_date, medical_history):
        return self.get(medical_history=medical_history,
                        start_date=start_date)


class MedicalDiagnosis(SiteModelMixin, BaseUuidModel):
    medical_history = models.ForeignKey(
        MedicalHistory,
        on_delete=models.PROTECT,
        verbose_name='Medical History Diagnosis',
        max_length=25)

    start_date = models.DateField(
        verbose_name='Start Date (DD/MMM/YYYY)',
        validators=[date_not_future])

    end_date = models.DateField(
        verbose_name='End Date (DD/MMM/YYYY)',
        null=True,
        blank=True)

    ongoing = models.CharField(
        verbose_name='Ongoing',
        choices=YES_NO,
        max_length=3)

    condition_related_meds = models.CharField(
        verbose_name='Is the subject taking medication related to this '
                     'condition?',
        choices=YES_NO,
        max_length=5)

    rel_conc_meds = models.TextField(
        max_length=150,
        verbose_name='Related concomitant medications',
        null=True,
        blank=True)

    history = HistoricalRecords()

    objects = MedicalDiagnosisManager()

    def natural_key(self):
        return (self.start_date,) + self.medical_history.natural_key()

    natural_key.dependencies = ['esr21_subject.medicalhistory']

    class Meta:
        app_label = 'esr21_subject'
        unique_together = ('medical_history', 'start_date', 'end_date')
        verbose_name = 'Medical Diagnosis'
        verbose_name_plural = 'Medical Diagnoses'
