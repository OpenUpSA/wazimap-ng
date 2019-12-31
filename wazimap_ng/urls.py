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
    path("api/v1/datasets/", dataset_views.DatasetList.as_view()),
    path("api/v1/datasets/<int:dataset_id>/indicators/", dataset_views.DatasetIndicatorsList.as_view()),
    path("api/v1/indicators/", dataset_views.IndicatorsList.as_view()),
    path("api/v1/indicators/<int:indicator_id>/", dataset_views.IndicatorDataView.as_view()),
    path("api/v1/indicators/<int:indicator_id>/geographies/<str:geography_code>/", dataset_views.IndicatorDataView.as_view()),
    path("api/v1/profiles/", dataset_views.ProfileList.as_view()),
    path("api/v1/profiles/<int:pk>/", dataset_views.ProfileDetail.as_view()),
    path("api/v1/profiles/<int:profile_id>/geographies/<str:geography_code>/", dataset_views.profile_geography_data),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
