from typing import List
import pytest
from wazimap_ng.datasets.models import Geography

from tests.datasets import factories


@pytest.fixture
def version() -> str:
    return "test_version"

@pytest.fixture
def geographies(version: str) -> List[Geography]:
    geo1 = Geography.add_root(code="geo_parent", name="geo_parent", level="parent_level", version=version)
    geo2 = geo1.add_child(code="geo2", name="geo2", level="test_level", version=version)
    geo3 = geo1.add_child(code="geo3", name="geo3", level="test_level", version=version)
    geo4 = geo1.add_child(code="geo4", name="geo4", level="test_level", version="other version")

    return [geo1, geo2, geo3, geo4]


@pytest.mark.django_db
class TestGetSiblings:
    def test_no_siblings(self, geographies: List[Geography]):
        _, _, _, geo4 = geographies

        siblings = geo4.get_siblings()
        assert len(siblings) == 1
        assert geo4 in siblings
        
    def test_only_correct_version_returned(self, geographies):
        geo1, geo2, geo3, _ = geographies
        siblings = geo2.get_siblings()

        assert len(siblings) == 2
        assert geo2 in siblings
        assert geo3 in siblings