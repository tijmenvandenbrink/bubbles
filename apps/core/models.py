from django.db import models


class Timestamped(models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True