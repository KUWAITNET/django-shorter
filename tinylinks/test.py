from django.contrib.auth.models import User
from models import Tinylink, TinylinkLog
from django.test import TestCase


class TinyLinkTest(TestCase):

    def setUp(self):
        Tinylink(long_url='')
