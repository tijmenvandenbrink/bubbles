from django.db import models

from taggit.managers import TaggableManager


class Organization(models.Model):
    name = models.CharField(max_length=75)
    org_id = models.IntegerField(unique=True)
    org_abbreviation = models.CharField(max_length=25)
    tags = TaggableManager(blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.org_id

        if not self.org_abbreviation:
            self.org_abbreviation = self.org_id

        super(Organization, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % self.name