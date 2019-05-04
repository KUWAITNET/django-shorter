"""
Utilities for creating test objects related to the ``django-tinylinks`` app.

"""
import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from ..models import Tinylink, TinylinkLog

User = get_user_model()


class TinylinkFactory(factory.Factory):
    class Meta:
        model = Tinylink

    long_url = "http://www.example.com/thisisalongURL"
    short_url = "vB7f5b"


class UserFactory(factory.Factory):
    """
    Factory for model User
    """
    class Meta:
        model = User

    username = 'test'
    email = 'gunjan@kuwaitnet.com'
    password = make_password('test1234')
    is_active = True
    is_superuser = True


class TinyLogFactory(factory.django.DjangoModelFactory):
    """
    Factory for model User
    """
    class Meta:
        model = TinylinkLog

    referrer = 'http://www.example.com/thisisalongURL'
    user_agent = 'Gunjan Modi'
    cookie = 'test:test'
    remote_ip = '127.0.0.1'
    tracked = True
