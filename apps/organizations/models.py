from django.db import models

from taggit.managers import TaggableManager

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=75)
    org_id = models.IntegerField(unique=True)
    org_abbreviation = models.CharField(max_length=25)
    tags = TaggableManager()

    def __unicode__(self):
        return "%s" % self.name