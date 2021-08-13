import pytest

from tests.points.factories import ThemeFactory, ProfileCategoryFactory
from tests.profile.factories import ProfileFactory


@pytest.fixture
def profile():
    return ProfileFactory()

@pytest.fixture
def theme():
    return ThemeFactory()

@pytest.fixture
def private_profile_theme(private_profile):
    return ThemeFactory(profile=private_profile)

@pytest.fixture
def profile_category(theme):
    return ProfileCategoryFactory(theme=theme, label="profile category name", description="my test profile category", color="red", profile=theme.profile)

