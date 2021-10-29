from django.db import models
from edc_base.model_fields import OtherCharField
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import date_not_future
from edc_base.sites import SiteModelMixin
from edc_constants.choices import SEVERITY_LEVEL, YES_NO

from .list_models import SAECriteria
from .model_mixins import CrfModelMixin


class SeriousAdverseEventRecordManager(models.Manager):

    def get_by_natural_key(self, sae_name, start_date, serious_adverse_event):
        return self.get(serious_adverse_event=serious_adverse_event,
                        sae_name=sae_name,
                        start_date=start_date)


class SeriousAdverseEvent(CrfModelMixin):
    """""Serious Adverse Events (SAE)"""""

    class Meta:
        app_label = 'esr21_subject'
        verbose_name = 'Serious Adverse Event'


class SeriousAdverseEventRecord(SiteModelMixin, BaseUuidModel):
    serious_adverse_event = models.ForeignKey(
        SeriousAdverseEvent,
        on_delete=models.PROTECT)

    ae_number = models.PositiveIntegerField(
        verbose_name='AE number',
        null=True
    )

    sae_name = models.CharField(
        verbose_name='AE reported term',
        max_length=100)

    sae_details = models.TextField(
        verbose_name='Details of the  SAE', )

    sae_criteria = models.ManyToManyField(SAECriteria, )

    dthcaus_1 = models.TextField(
        verbose_name='Primary cause of death',
        blank=True,
        null=True
    )

    dthcaus_2 = models.TextField(
        verbose_name='Secondary cause of death',
        blank=True,
        null=True
    )

    ae_sautop = models.CharField(
        verbose_name='Was an autopsy performed?',
        max_length=10,
        choices=YES_NO
    )

    ae_caad = models.CharField(
        verbose_name='Did the event abate after drug discontinuation?',
        max_length=10,
        choices=YES_NO,
    )

    ae_add_drug = models.CharField(
        verbose_name='If yes above, please provide additional drug',
        max_length=10,
        blank=True,
        null=True
    )

    ae_smedca = models.CharField(
        verbose_name='Was SAE caused by other medication?',
        max_length=10,
        choices=YES_NO,
    )

    ae_smed = models.CharField(
        verbose_name='Other Medication',
        max_length=200,
        blank=True,
        null=True
    )

    ae_caussp = models.CharField(
        verbose_name='Was SAE caused by study procedure(s)?',
        max_length=5,
        choices=YES_NO,
    )

    ae_sp = models.CharField(
        verbose_name='Study Procedure(s)',
        max_length=200,
        blank=True,
        null=True
    )

    sae_intensity = models.CharField(
        verbose_name='Intensity of the SAE',
        choices=SEVERITY_LEVEL,
        max_length=10)

    start_date = models.DateField(
        verbose_name='Date AE Met Criteria for Serious AE',
        validators=[date_not_future, ])

    resolution_date = models.DateField(
        verbose_name='SAE end date',
        validators=[date_not_future, ],
        null=True,
        blank=True)

    date_aware_of = models.DateField(
        verbose_name="Date investigator became aware of SAE",
        validators=[date_not_future, ])

    ae_sdth = models.CharField(
        verbose_name='Results in death?',
        max_length=3,
        choices=YES_NO
    )

    ae_shosp = models.CharField(
        verbose_name='Does it require or prolong hospitalization?',
        max_length=3,
        choices=YES_NO,
    )

    ae_scong = models.CharField(
        verbose_name='Was it a congenital anomaly or birth defect?',
        max_length=6,
        choices=YES_NO,
    )

    ae_slife = models.CharField(
        verbose_name='Was adverse even it life threatening?',
        max_length=6,
        choices=YES_NO
    )

    ae_sdisab = models.CharField(
        verbose_name='Was it persistent or resulting in significant disability/incapacity? ',
        max_length=6,
        choices=YES_NO
    )

    ae_smie = models.CharField(
        verbose_name='Are there other medically important serious event?',
        max_length=6,
        choices=YES_NO
    )

    admission_date = models.DateField(
        verbose_name='Date of hospitalization',
        validators=[date_not_future, ],
        null=True,
        blank=True)

    discharge_date = models.DateField(
        verbose_name='If hospitalized, Date of Discharge',
        null=True,
        blank=True)

    incapacity_specify = OtherCharField(
        verbose_name='Specify persistent or significant disability/incapacity',
        max_length=100)

    medical_event_other = OtherCharField(
        verbose_name='If, Other important medical event, specify',
        null=True,
        blank=True,
        max_length=100)

    rationale = models.CharField(
        verbose_name=('Investigator\'s rationale for Study Treatment being '
                      'Related to the events'),
        max_length=100)

    describe_sae_treatmnt = models.TextField(
        verbose_name='Describe treatment for event including medications',
        null=True,
        blank=True,
        max_length=200)

    test_performed = models.TextField(
        verbose_name='List all diagnostic tests that were performed to confirm event',
        null=True,
        blank=True,
        max_length=200)

    additional_info = models.TextField(
        verbose_name=('Additional information (for example: history of '
                      'presenting illness, course of illness, complications, '
                      'risk factors and/or other contributing factors)'),
        null=True,
        blank=True,
        max_length=200)

    event_abate = models.TextField(
        verbose_name='List all diagnostic tests that were performed to confirm event',
        max_length=200)

    history = HistoricalRecords()

    objects = SeriousAdverseEventRecordManager()

    def natural_key(self):
        return (self.sae_name, self.start_date,) + self.serious_adverse_event.natural_key()

    natural_key.dependencies = ['esr21_subject.seriousadverseevent']

    class Meta:
        app_label = 'esr21_subject'
        unique_together = ('serious_adverse_event', 'start_date', 'date_aware_of')
        verbose_name = 'Serious Adverse Event Record'
