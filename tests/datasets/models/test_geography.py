from typing import List
import pytest
from wazimap_ng.datasets.models import Geography

from tests.datasets import factories
from tests.boundaries.factories import GeographyBoundaryFactory


@pytest.fixture
def version() -> str:
    return "test_version"

@pytest.fixture
def geographies(version: str) -> List[Geography]:
    geo1 = Geography.add_root(code="geo_parent", name="geo_parent", level="parent_level", version=version)
    geo2 = geo1.add_child(code="geo2", name="geo2", level="test_level", version=version)
    geo3 = geo1.add_child(code="geo3", name="geo3", level="test_level", version=version)
    geo4 = geo1.add_child(code="geo4", name="geo4", level="test_level", version="other version")
    geo5 = geo1.add_child(code="geo4", name="geo4", level="test_level2", version=version)
    
    for geo in [geo1, geo2, geo3, geo4, geo5]:
        boundary = GeographyBoundaryFactory(geography=geo)

    return [geo1, geo2, geo3, geo4, geo5]


@pytest.mark.django_db
class TestGetSiblings:
    def test_no_siblings(self, geographies: List[Geography]):
        _, _, _, geo4, _ = geographies

        siblings = geo4.get_siblings()
        assert len(siblings) == 1
        assert geo4 in siblings
        
    def test_only_correct_version_returned(self, geographies):
        geo1, geo2, geo3, _, geo5 = geographies
        siblings = geo2.get_siblings()

        assert len(siblings) == 3
        assert geo2 in siblings
        assert geo3 in siblings
        assert geo5 in siblings

@pytest.mark.django_db
class TestGetChildBoundaries:
    def test_get_correct_boundaries(self, geographies: List[Geography]):
        geo1, geo2, geo3, _, geo5 = geographies
        boundaries = geo1.get_child_boundaries()
        assert len(boundaries.keys()) == 2

        level = geo2.level
        assert level in boundaries
        assert len(boundaries[level]) == 2


        level = geo5.level
        assert level in boundaries
        assert len(boundaries[level]) == 1
        
    def test_handles_no_children_correctly(self, geographies: List[Geography]):
        _, geo2, _, _, _ = geographies
        boundaries = geo2.get_child_boundaries()
        assert len(boundaries.keys()) == 0