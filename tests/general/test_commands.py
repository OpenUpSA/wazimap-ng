from django.core.management import call_command
from django.test import TestCase

from wazimap_ng.datasets.models import Dataset
import pytest

@pytest.mark.focus
class LoadInitialData(TestCase):
    def test_should_create_all_datasets(self):
        call_command('load_data')
        self.assertTrue(Dataset.objects.all().exists())
        self.assertEqual(len(Dataset.objects.all()),2)
