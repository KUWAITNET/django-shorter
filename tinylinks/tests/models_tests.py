"""Tests for the models of the ``django-tinylinks`` app."""
from urllib2 import urlopen, URLError

from django.test import TestCase
from django.utils import timezone

from tinylinks.models import validate_long_url, Tinylink
from tinylinks.tests.factories import TinylinkFactory


class TinylinkTestCase(TestCase):
    """Tests for the ``Tinylink`` model class."""
    def test_model(self):
        obj = TinylinkFactory()
        self.assertTrue(obj.pk)

        link = TinylinkFactory(long_url="http://www.google.com/",
                               short_url="v4bG4S")
        validate_long_url(link)
        self.assertEqual(Tinylink.objects.get(pk=link.pk).validation_error, "")
        link.long_url = "http://www.a1b2c3d4e5000.com/"
        link.save()
        validate_long_url(link)
        self.assertEqual(Tinylink.objects.get(pk=link.pk).validation_error,
                         "URL not accessible.")
        #---------------------------------------------
        # IMPORTANT: Start runserver before testing.
        #---------------------------------------------
        try:
            urlopen('http://localhost:8000/admin/')
        except URLError:
            self.fail('Start runserver before testing.')
        link.long_url = "http://localhost:8000/redirect-fail/"
        link.save()
        validate_long_url(link)
        self.assertTrue(Tinylink.objects.get(pk=link.pk).is_broken)
        link.long_url = "http://localhost:8000/redirect-test/"
        link.save()
        validate_long_url(link)
        self.assertTrue(Tinylink.objects.get(pk=link.pk).is_broken)

        link.last_checked = timezone.now() - timezone.timedelta(minutes=61)
        self.assertTrue(link.can_be_validated())
