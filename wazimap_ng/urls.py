from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic.base import RedirectView

from .datasets import views as dataset_views


urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"admin$", RedirectView.as_view(url="admin/", permanent=True)),
    path("api/v1/datasets/", dataset_views.DatasetList.as_view(), name="dataset"),
    path(
        "api/v1/datasets/<int:dataset_id>/indicators/",
        dataset_views.DatasetIndicatorsList.as_view(),
        name="dataset-indicator-list",
    ),
    path(
        "api/v1/indicators/",
        dataset_views.IndicatorsList.as_view(),
        name="indicator-list",
    ),
    path(
        "api/v1/indicators/<int:indicator_id>/",
        dataset_views.IndicatorDataView.as_view(),
        name="indicator-data-view",
    ),
    path(
        "api/v1/indicators/<int:indicator_id>/geographies/<str:geography_code>/",
        dataset_views.IndicatorDataView.as_view(),
        name="indicator-data-view-geography",
    ),
    path("api/v1/profiles/", dataset_views.ProfileList.as_view(), name="profile-list"),
    path(
        "api/v1/profiles/<int:pk>/",
        dataset_views.ProfileDetail.as_view(),
        name="profile-detail",
    ),
    path(
        "api/v1/profiles/<int:profile_id>/geographies/<str:geography_code>/",
        dataset_views.profile_geography_data,
        name="profile-geography-data",
    ),
    re_path(r"^$", RedirectView.as_view(url="/api/v1/datasets/", permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
