import pytest

from tests.points.factories import ThemeFactory, ProfileCategoryFactory
from tests.profile.factories import ProfileFactory


@pytest.fixture
def theme(profile):
    return ThemeFactory(profile=profile)

@pytest.fixture
def profile_category(theme):
    return ProfileCategoryFactory(theme=theme, label="profile category name", description="my test profile category", color="red", profile=theme.profile)