from django.test import TestCase

from wazimap_ng.profile.models import Profile
from wazimap_ng.boundaries.models import GeographyBoundary
from wazimap_ng.datasets.models.dataset import Dataset
from wazimap_ng.datasets.models.geography import Geography
from wazimap_ng.points.models import Category, Theme

class SiteTests(TestCase):
    fixtures = ['demodata.json']

    def testProfile(self):
        profile = Profile.objects.get(pk=1)
        self.assertEquals(profile.name, 'Demo profile')
        
    def testBoundaries(self):
        boundary = GeographyBoundary.objects.get(pk=1)
        self.assertIsNotNone(boundary.geography)

    def testDataset(self):
        geography = Geography.objects.get(pk=1)
        self.assertEquals(geography.name, 'South Africa')
        
        dataset = Dataset.objects.get(pk=1)
        self.assertEquals(dataset.name, 'Population dataset')
    
    def testPoints(self):
        collection = Category.objects.get(pk=1)
        self.assertEquals(collection.name, 'University collection')
        
        theme = Theme.objects.get(pk=1)
        self.assertEquals(theme.name, 'Education theme')
        

