from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from .users.views import UserViewSet, UserCreateViewSet
from .datasets import views as dataset_views
from .ui.views import UIView

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"users", UserCreateViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"ui", UIView.as_view(), name="ui"),
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("ui"), permanent=False)),
    path("api/v1/", include(router.urls)),
    path("api/v1/datasets/", dataset_views.datasets),
    path("api/v1/datasets/<int:dataset_id>/", dataset_views.dataset_meta),
    path("api/v1/datasets/<int:dataset_id>/indicators/", dataset_views.dataset_indicators),
    path("api/v1/indicators/", dataset_views.indicators),
    path("api/v1/indicators/<int:indicator_id>/", dataset_views.indicator_raw_data),
    path("api/v1/indicators/<int:indicator_id>/geographies/<int:geography_id>/", dataset_views.indicator_geography),
    path("api/v1/profiles/", dataset_views.profiles),
    path("api/v1/profiles/<int:profile_id>/", dataset_views.profile_indicators),
    path("api/v1/profiles/<int:profile_id>/geographies/<str:geography_code>/", dataset_views.profile_geography_data),
    path(r'select2/', include('django_select2.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
