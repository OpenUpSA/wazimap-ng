import factory
from wazimap_ng.profile import models


class ProfileFactory(factory.Factory):
    class Meta:
        model = models.Profile
