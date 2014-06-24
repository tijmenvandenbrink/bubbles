from haystack import indexes
from apps.devices.models import Device


class DeviceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    software_version = indexes.CharField(model_attr='software_version')
    device_type = indexes.CharField(model_attr='device_type')
    ip = indexes.CharField(model_attr='ip')

    def get_model(self):
        return Device

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()