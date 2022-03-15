import pytest

from django.urls import reverse


@pytest.mark.django_db
class TestProfileVersions:
    def test_public_profile_versions_for_anonymous_user(
        self, client, profile, version
    ):
        url = reverse("profile-versions", args=(profile.id,))
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == version.id
        assert response.data[0]["name"] == version.name

    def test_private_profile_versions_for_anonymous_user(
        self, client, private_profile
    ):
        url = reverse("profile-versions", args=(private_profile.id,))
        response = client.get(url, follow=True)
        assert response.status_code == 401
        assert str(response.data["detail"]) == "Authentication credentials were not provided."

    def test_private_profile_versions_for_superuser(
        self, client, superuser, private_profile, version
    ):
        client.force_login(user=superuser)
        url = reverse("profile-versions", args=(private_profile.id,))
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == version.id
        assert response.data[0]["name"] == version.name

    def test_private_profile_versions_for_dataadmin(
        self, client, data_admin_user, private_profile, version
    ):
        client.force_login(user=data_admin_user)
        url = reverse("profile-versions", args=(private_profile.id,))
        response = client.get(url, follow=True)
        assert response.status_code == 403
        assert str(response.data["detail"]) == "You do not have permission to perform this action."

    def test_private_profile_versions_for_dataadmin_with_permissions(
        self, client, data_admin_user, private_profile, version,
        private_profile_group
    ):
        data_admin_user.groups.add(private_profile_group)
        client.force_login(user=data_admin_user)
        url = reverse("profile-versions", args=(private_profile.id,))
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == version.id
        assert response.data[0]["name"] == version.name
