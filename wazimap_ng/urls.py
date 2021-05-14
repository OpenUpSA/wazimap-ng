from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include

from django.views.generic.base import RedirectView
from rest_framework.decorators import api_view

from rest_framework.response import Response

from .datasets import views as dataset_views
from .points import views as points_views
from .profile import views as profile_views
from .boundaries import views as boundaries_views
from .general import views as general_views
from .cache import cache_headers as cache

from wazimap_ng.general.views import logout_view, notifications_view

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),
    path("admin/notifications", notifications_view, name="notifications"),

    # Api
    path("api/v1/rest-auth/", include("rest_auth.urls")),
    path("api/v1/datasets/", dataset_views.DatasetList.as_view(), name="dataset"),
    path(
        "api/v1/datasets/<int:pk>/", dataset_views.DatasetDetailView.as_view(),
        name="dataset-detail"
    ),
    path(
        "api/v1/datasets/<int:dataset_id>/upload/", dataset_views.dataset_upload,
        name="dataset-upload"
    ),
    path("api/v1/universe/", dataset_views.UniverseListView.as_view(), name="universe"),
    path(
        "api/v1/datasets/<int:dataset_id>/indicators/",
        cache(dataset_views.DatasetIndicatorsList.as_view()),
        name="dataset-indicator-list",
    ),
    path(
        "api/v1/indicators/",
        cache(dataset_views.IndicatorsList.as_view()),
        name="indicator-list",
    ),
    path(
        "api/v1/indicators/<int:pk>/",
        cache(dataset_views.IndicatorDetailView.as_view()),
        name="indicator-detail",
    ),
    path(
        "api/v1/geography/hierarchies/",
        cache(dataset_views.GeographyHierarchyViewset.as_view({"get":"list"})),
        name="geography-hierarchies",
    ),
    path(
        "api/v1/geography/hierarchies/<int:pk>/",
        cache(dataset_views.GeographyHierarchyViewset.as_view({"get":"retrieve"})),
        name="geography-hierarchies",
    ),
    path("api/v1/profiles/", profile_views.ProfileList.as_view(), name="profile-list"),
    path("api/v1/profile_by_url/", profile_views.ProfileByUrl.as_view(), name="profile-by-url"),
    path(
        "api/v1/profiles/<int:pk>/",
        cache(profile_views.ProfileDetail.as_view()),
        name="profile-detail",
    ),
    path(
        "api/v1/profiles/<int:profile_id>/categories/",
        cache(profile_views.ProfileCategoriesList.as_view()),
        name="profile-categories",
    ),
    path(
        "api/v1/profiles/<int:profile_id>/categories/<int:category_id>/",
        cache(profile_views.ProfileSubcategoriesByCategoryList.as_view()),
        name="profile-subcategories",
    ),
    path(
        "api/v1/profiles/<int:profile_id>/subcategories/",
        cache(profile_views.ProfileSubcategoriesList.as_view()),
        name="profile-subcategories-list",
    ),
    path(
        "api/v1/profiles/<int:profile_id>/geographies/<str:geography_code>/",
        cache(profile_views.profile_geography_data),
        name="profile-geography-data",
    ),
    path(
        "api/v1/profile/<int:profile_id>/geography/<str:geography_code>/",
        cache(profile_views.profile_geography_data),
        name="profile-geography-data",
    ),
    path(
        "api/v1/profile/<int:profile_id>/geography/<str:geography_code>/indicator/<int:profile_indicator_id>/",
        profile_views.profile_geography_indicator_data,
        name="profile-geography-indicator-data",
    ),
    path("api/v1/geography/search/<str:profile_id>/", cache(dataset_views.search_geography)),
    path("api/v1/geography/ancestors/<str:geography_code>/<str:version>/", cache(dataset_views.geography_ancestors), name="geography-ancestors"),

    path("api/v1/profile/<int:profile_id>/points/themes/", cache(points_views.ThemeList.as_view()), name="points-themes"),
    path("api/v1/profile/<int:profile_id>/points/themes/categories/", cache(points_views.ProfileCategoryList.as_view())),
    path("api/v1/profile/<int:profile_id>/points/category/<int:profile_category_id>/points/", cache(points_views.LocationList.as_view()), name="category-points"),
    path("api/v1/profile/<int:profile_id>/points/geography/<str:geography_code>/points/", cache(points_views.GeoLocationList.as_view()), name="geography-points"),
    path("api/v1/profile/<int:profile_id>/points/category/<int:profile_category_id>/geography/<str:geography_code>/points/", cache(points_views.LocationList.as_view()), name="category-points-geography"),
    path("api/v1/profile/<int:profile_id>/points/profile_categories/", cache(points_views.ProfileCategoryList.as_view()), name="profile-category"),
    path("api/v1/profile/<int:profile_id>/points/theme/<int:theme_id>/profile_categories/", cache(points_views.ProfileCategoryList.as_view()), name="profile-category-theme"),

    re_path(r"^$", RedirectView.as_view(url="/api/v1/datasets/", permanent=False)),
    path("api/v1/data/points/collections/", cache(points_views.CategoryList.as_view())),
    path("api/v1/data/points/collections/profile/<int:profile_id>", cache(points_views.CategoryList.as_view())),
    

    path(
        "api/v1/boundaries/",
        cache(boundaries_views.GeographyList.as_view()),
        name="boundaries"
    ),

    path(
        "api/v1/boundaries/<str:code>/",
        cache(boundaries_views.GeographyItem.as_view()),
        name="boundaries-code"
    ),

    path(
        "api/v1/boundaries/<str:code>/<str:version>/",
        cache(boundaries_views.GeographyItem.as_view()),
        name="boundaries-code"
    ),

    path(
        "api/v1/boundaries/<str:code>/<str:version>/children/",
        cache(boundaries_views.GeographyChildren.as_view()),
        name="boundaries-children"
    ),
    #path("api/v1/boundaries/provinces/", boundaries_views.provinces),

    path(
        "api/v1/all_details/profile/<int:profile_id>/geography/<str:geography_code>/",
        cache(general_views.consolidated_profile),
        name="all-details"
    ),

    path(
        "api/v1/all_details/profile/<int:profile_id>/geography/<str:geography_code>/test/",
        cache(general_views.consolidated_profile_test),
        name="all-details-test"
    ),
    path('sentry-debug/', trigger_error),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
