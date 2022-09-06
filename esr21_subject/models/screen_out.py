from django.db import models
from edc_base.utils import get_utcnow
from edc_base.model_validators.date import datetime_not_future
from edc_identifier.model_mixins import UniqueSubjectIdentifierModelMixin
from edc_protocol.validators import datetime_not_before_study_start
from edc_base.model_mixins import BaseUuidModel
from .model_mixins import SearchSlugModelMixin
from edc_base.model_managers import HistoricalRecords
from edc_base.model_fields import OtherCharField


from edc_search.model_mixins import SearchSlugManager
from edc_base.sites import SiteModelMixin
from ..choices import SCREENOUT_CHOICES


class ScreenOutManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)

class ScreenOut(UniqueSubjectIdentifierModelMixin, SiteModelMixin,
                         SearchSlugModelMixin, BaseUuidModel):
    """A model for screening failures
    """
    
    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow,
        help_text=('If reporting today, use today\'s date/time, otherwise use '
                    'the date/time this information was reported.'))

    screen_out_reason = models.CharField(
        verbose_name='What is the reason for screening failure',
        choices=SCREENOUT_CHOICES,
        max_length=25,
        help_text="If 'OTHER', specify below"   
    )
    
    screen_out_other = OtherCharField()
    
    comment = models.TextField(
        verbose_name="Comment if any additional pertinent information ",
        max_length=250,
        blank=True,
        null=True)

    history = HistoricalRecords()
    
    objects = ScreenOutManager()
    
    def __str__(self):
        return self.subject_identifier

    def natural_key(self):
        return (self.subject_identifier,)

    natural_key.dependencies = ['sites.Site']
    
    class Meta:
        app_label = 'esr21_subject'
        verbose_name = 'Screening Out'
        verbose_name_plural = 'Screen Outs'
