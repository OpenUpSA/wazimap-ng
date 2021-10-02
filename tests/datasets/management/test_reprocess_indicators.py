import pytest
from django.core.management import call_command
from django_q.models import Task
from wazimap_ng.datasets.models import Indicator
from wazimap_ng.datasets.management.commands import reprocess_indicators

@pytest.mark.django_db
@pytest.mark.usefixtures("indicator")
class TestReprocessIndicators:

    def test_reprocess_indicators(self):
        args = []
        opts = {}
        assert Task.objects.filter(success=True).count() == 0
        assert Indicator.objects.count() == 1
        indicator_obj = Indicator.objects.first()

        reprocess_indicators.input = lambda x: 'yes'
        call_command('reprocess_indicators', *args, **opts)

        assert Task.objects.filter(success=True).count() == 1
        task = Task.objects.filter(success=True).first()
        assert task.args[0] == indicator_obj
        assert task.kwargs["type"] == "data_extraction"


