"""Test views for the ``django-tinylinks`` application."""
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View


class TestFailedRedirectView(View):
    def dispatch(self, *args, **kwargs):
        raise Http404


class TestRedirectView(View):
    def dispatch(self, *args, **kwargs):
        return HttpResponseRedirect(reverse('tinylink_create'))
