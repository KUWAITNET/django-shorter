"""
This ``urls.py`` is only used when running the tests via ``runtests.py``.
As you know, every app must be hooked into yout main ``urls.py`` so that
you can actually reach the app's views (provided it has any views, of course).

"""
from django.conf.urls import include, patterns, url
from django.contrib import admin

from tinylinks.tests.views import TestFailedRedirectView, TestRedirectView


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^redirect-test/', TestRedirectView.as_view()),
    url(r'^redirect-fail/', TestFailedRedirectView.as_view()),
    url(r'^administration/', include(admin.site.urls)),
    url(r'^s/', include('tinylinks.urls')),
)
