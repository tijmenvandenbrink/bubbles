from haystack import indexes
from apps.services.models import Service


class ServiceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    organization = indexes.CharField(model_attr='organization')
    service_type = indexes.CharField(model_attr='service_type')
    status = indexes.CharField(model_attr='status__name')

    def get_model(self):
        return Service

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
