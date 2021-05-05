import operator
from functools import reduce

from django.http import Http404
from django.views.decorators.http import condition
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from django_q.tasks import async_task

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_csv import renderers as r
from rest_framework import generics, viewsets, status

from .serializers import AncestorGeographySerializer
from . import serializers
from . import models
from ..cache import etag_profile_updated, last_modified_profile_updated
from ..profile.models import Logo
from ..utils import truthy

from wazimap_ng.profile.models import Profile
from wazimap_ng.general.services.permissions import assign_perms_to_group

class DatasetList(generics.ListCreateAPIView):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer


    def post(self, request, *args, **kwargs):
        profile_id = request.data.get("profile")
        profile = get_object_or_404(Profile, pk=profile_id)
        if not request.user.groups.filter(name=profile.name).exists():
            return Response({
                    'detail': 'You do not have permission to upload to this profile'
                }, status=status.HTTP_403_FORBIDDEN
            )
        response = self.create(request, *args, **kwargs)

        dataset_obj = models.Dataset.objects.filter(id=response.data["id"]).first()

        # Assign dataset object permission to profile group
        assign_perms_to_group(profile.name, dataset_obj, False)

        # Get and create dataset file if user has sent file while creating dataset
        file_obj = request.data.get('file', None)
        if file_obj:
            datasetfile_obj = models.DatasetFile.objects.create(
                name=dataset_obj.name,
                document=file_obj,
                dataset_id=dataset_obj.id
            )

            task = async_task(
                "wazimap_ng.datasets.tasks.process_uploaded_file",
                datasetfile_obj, dataset_obj,
                task_name=f"Uploading data: {dataset_obj.name}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="upload", assign=True, notify=True, email=True,
                user_id=request.user.id
            )
            response.data["upload_task_id"] = task

        return response

class DatasetDetailView(generics.RetrieveAPIView):
    queryset = models.Dataset
    serializer_class = serializers.DatasetDetailViewSerializer


@api_view(['POST'])
def dataset_upload(request, dataset_id):
    dataset = get_object_or_404(models.Dataset, pk=dataset_id)

    if not request.user.groups.filter(name=dataset.profile.name).exists():
        return Response({
                'detail': 'You do not have permission to upload to this profile'
            }, status=status.HTTP_403_FORBIDDEN
        )
    file_obj = request.data.get('file', None)

    if not file_obj:
        return Response({
                'detail': 'please add file for upload'
            }, status=status.HTTP_403_FORBIDDEN
        )
    response = serializers.DatasetDetailViewSerializer(dataset).data

    datasetfile_obj = models.DatasetFile.objects.create(
        name=dataset.name,
        document=file_obj,
        dataset_id=dataset.id
    )
    update_indicators = request.POST.get('update', False)
    overwrite = request.POST.get('overwrite', False)

    upload_task = async_task(
        "wazimap_ng.datasets.tasks.process_uploaded_file",
        datasetfile_obj, dataset, overwrite=overwrite,
        task_name=f"Uploading data: {dataset.name}",
        hook="wazimap_ng.datasets.hooks.process_task_info",
        key=request.session.session_key,
        type="upload", assign=True, notify=False,
        update_indicators=update_indicators, email=True,
        user_id=request.user.id
    )

    response["upload_task_id"] = upload_task
    return Response(response, status=status.HTTP_200_OK)


class UniverseListView(generics.ListAPIView):
    queryset = models.Universe.objects.all()
    serializer_class = serializers.UniverseViewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        dataset = self.request.query_params.get('dataset', None)
        group = self.request.query_params.get('group', None)

        dataset = models.Dataset.objects.filter(id=dataset).first()
        if not dataset:
            return queryset

        if not dataset.groups:
            return models.Universe.objects.none()

        groups = dataset.groups
        if group:
            groups = [group]

        # condition = reduce(
        #     operator.or_, [Q(as_string__icontains=group) for group in groups]
        # )

        # return queryset.annotate(
        #     as_string=Cast('filters', CharField())
        # ).filter(condition)

        return queryset.annotate(
            as_string=Cast('filters', CharField())
        )

class DatasetIndicatorsList(generics.ListAPIView):
    queryset = models.Indicator.objects.all()
    serializer_class = serializers.IndicatorSerializer

    def get(self, request, dataset_id):
        if models.Dataset.objects.filter(id=dataset_id).count() == 0:
            raise Http404 

        queryset = self.get_queryset().filter(dataset=dataset_id)
        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class IndicatorsList(generics.ListAPIView):
    queryset = models.Indicator.objects.all()
    serializer_class = serializers.IndicatorSerializer

class IndicatorDetailView(generics.RetrieveAPIView):
    queryset = models.Indicator
    serializer_class = serializers.IndicatorSerializer


class GeographyHierarchyViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.GeographyHierarchy.objects.all()
    serializer_class = serializers.GeographyHierarchySerializer


@api_view()
def search_geography(request, profile_id):
    """
    Search autocompletion - provides recommendations from place names
    Prioritises higher-level geographies in the results, e.g. 
    Provinces of Municipalities. 

    Querystring parameters
    q - search string
    max-results number of results to be returned [default is 30] 
    """
    profile = get_object_or_404(Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    
    default_results = 30
    max_results = request.GET.get("max_results", default_results)
    try:
        max_results = int(max_results)
        if max_results <= 0:
            max_results = default_results
    except ValueError:
        max_results = default_results

    q = request.GET.get("q", "")

    geographies = models.Geography.objects.filter(version=version).search(q)[0:max_results]

    def sort_key(x):
        exact_match = x.name.lower() == q.lower()
        if exact_match:
            return 0

        else:
            # TODO South Africa specific geography 
            return {
                "province": 1,
                "district": 2,
                "municipality": 3,
                "mainplace": 4,
                "subplace": 5,
                "ward": 6,
            }.get(x.level, 7)

    geogs = sorted(geographies, key=sort_key)
    serializer = serializers.AncestorGeographySerializer(geogs, many=True)

    return Response(serializer.data)

@api_view()
def geography_ancestors(request, geography_code, version):
    """
    Returns parent geographies of the given geography code
    Return a 404 HTTP response if the is the code is not found
    """
    geos = models.Geography.objects.filter(code=geography_code, version=version)
    if geos.count() == 0:
        raise Http404 

    geography = geos.first()
    geo_js = AncestorGeographySerializer().to_representation(geography)

    return Response(geo_js)
