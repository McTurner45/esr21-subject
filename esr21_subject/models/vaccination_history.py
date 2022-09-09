from django.db import models
from edc_base.model_fields import OtherCharField
from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_managers import HistoricalRecords

from edc_constants.choices import YES_NO
from edc_base.utils import get_utcnow
from edc_base.model_validators import datetime_not_future, date_not_future
from edc_base.sites import SiteModelMixin

from .model_mixins import SearchSlugModelMixin
from ..choices import DOSE_QUANTITY, COVID_PRODUCT_NAME, COVID_INFO_SOURCE


class VaccinationHistoryManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class VaccinationHistory(UniqueSubjectIdentifierModelMixin, SiteModelMixin,
                         SearchSlugModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(
        verbose_name='Report Date and Time',
        default=get_utcnow,
        validators=[datetime_not_future],
        help_text='Date and time of report.')

    received_vaccine = models.CharField(
        verbose_name='Did the participant receive a COVID-19 vaccine?',
        choices=YES_NO,
        max_length=3, )

    dose_quantity = models.CharField(
        verbose_name='Number of doses received?',
        choices=DOSE_QUANTITY,
        max_length=1,
        blank=True,
        null=True, )

    dose1_product_name = models.CharField(
        verbose_name='Product name of COVID-19 vaccine dose 1',
        choices=COVID_PRODUCT_NAME,
        max_length=12,
        blank=True,
        null=True, )

    dose1_product_other = OtherCharField()

    dose1_date = models.DateField(
        verbose_name='Date of vaccine dose 1',
        validators=[date_not_future, ],
        blank=True,
        null=True, )

    dose2_product_name = models.CharField(
        verbose_name='Product name of COVID-19 vaccine dose 2',
        choices=COVID_PRODUCT_NAME,
        max_length=12,
        blank=True,
        null=True, )

    dose2_product_other = OtherCharField()

    dose2_date = models.DateField(
        verbose_name='Date of vaccine dose 2',
        validators=[date_not_future, ],
        blank=True,
        null=True, )

    dose3_product_name = models.CharField(
        verbose_name='Product name of COVID-19 vaccine dose 3',
        choices=COVID_PRODUCT_NAME,
        max_length=12,
        blank=True,
        null=True, )

    dose3_product_other = OtherCharField()

    dose3_date = models.DateField(
        verbose_name='Date of vaccine dose 3',
        validators=[date_not_future, ],
        blank=True,
        null=True, )

    source_of_info = models.CharField(
        verbose_name='Primary source of information',
        choices=COVID_INFO_SOURCE,
        default='documented_evidence',
        max_length=22, )

    objects = VaccinationHistoryManager()

    history = HistoricalRecords()

    def __str__(self):
        return self.subject_identifier

    def natural_key(self):
        return (self.subject_identifier,)

    natural_key.dependencies = ['sites.Site']

    class Meta:
        app_label = 'esr21_subject'
        verbose_name = 'Vaccination History'
        verbose_name_plural = 'Vaccination History'
