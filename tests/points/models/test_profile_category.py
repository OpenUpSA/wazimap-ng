import pytest

from tests.points.factories import (
    ProfileCategoryFactory, CategoryFactory, LocationFactory
)
from tests.profile.factories import ProfileFactory

@pytest.mark.django_db
class TestProfileCategory:
    def test_single_location_attributes(self):
        data = [{ "key": "attribute1",  "value": "value1"}]
        loc = LocationFactory(data=data)
        pf = ProfileCategoryFactory(category=loc.category)

        assert pf.location_attributes == ["attribute1"]

    def test_multiple_location_attributes(self):
        data = [{ "key": "attribute1",  "value": "value1"}, {"key": "attribute2", "value": "value2"}]
        loc = LocationFactory(data=data)
        pf = ProfileCategoryFactory(category=loc.category)

        assert len(pf.location_attributes) == 2
        assert "attribute1" in pf.location_attributes
        assert "attribute2" in pf.location_attributes

    def test_multiple_locations_attributes(self):
        data = [{ "key": "attribute1",  "value": "value1"}, {"key": "attribute2", "value": "value2"}]
        data2 = [{ "key": "attribute1",  "value": "value1"}, {"key": "attribute3", "value": "value2"}]
        loc = LocationFactory(data=data)
        loc1 = LocationFactory(data=data2, category=loc.category)
        pf = ProfileCategoryFactory(category=loc.category)

        assert len(pf.location_attributes) == 3
        assert "attribute1" in pf.location_attributes
        assert "attribute2" in pf.location_attributes
        assert "attribute3" in pf.location_attributes
