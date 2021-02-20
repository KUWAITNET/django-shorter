"""URLs for the ``django-tinylinks`` app."""
from django.conf import settings
from django.conf.urls import include
from django.urls import re_path
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from tinylinks.utils.router import CustomDefaultRouter
from tinylinks.views import (
    StatisticsView,
    TinylinkCreateView,
    TinylinkDeleteView,
    TinylinkListView,
    TinylinkRedirectView,
    TinylinkUpdateView,
    TinylinkViewSet,
    UserViewSet,
    db_stats,
    stats,
    tinylink_stats,
    tinylink_expand,
)

# Create router and register our API viewsets with it.
router = CustomDefaultRouter()
router.register(
    r"{}".format(getattr(settings, "TINYLINK_API_PREFIX", "tinylinks")), TinylinkViewSet
)
router.register(r"users", UserViewSet)

urlpatterns = [
    re_path(r"^list/$", TinylinkListView.as_view(), name="tinylink_list"),
    re_path(r"^create/$", TinylinkCreateView.as_view(), name="tinylink_create"),
    re_path(
        r"^update/(?P<pk>\d+)/(?P<mode>[a-z-]+)/$",
        TinylinkUpdateView.as_view(),
        name="tinylink_update",
    ),
    re_path(
        r"^delete/(?P<pk>\d+)/$",
        TinylinkDeleteView.as_view(),
        name="tinylink_delete",
    ),
]

if getattr(settings, "TINYLINK_REDIRECT_404", None):
    urlpatterns += [
        re_path(
            r"^404/$",
            RedirectView.as_view(permanent=False, url=settings.TINYLINK_REDIRECT_404),
            name="tinylink_notfound",
        ),
    ]
else:
    urlpatterns += [
        re_path(
            r"^404/$",
            TemplateView.as_view(template_name="tinylinks/notfound.html"),
            name="tinylink_notfound",
        ),
    ]

urlpatterns += [
    re_path(
        r"^statistics/?$",
        StatisticsView.as_view(),
        name="tinylink_statistics",
    ),
    re_path(
        r"^api/",
        include(router.urls),
    ),
    re_path(
        r"^auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
    re_path(r"^api/db-stats/$", db_stats, name="api_db_stats"),
    re_path(r"^api/stats/$", stats, name="api_stats"),
    re_path(
        r"^api/url-stats/(?P<short_url>\w+)/", tinylink_stats, name="api_url_stats"
    ),
    re_path(
        r"^api/expand/(?P<short_url>\w+)/$", tinylink_expand, name="api_tinylink_expand"
    ),
    re_path(
        r"^(?P<short_url>[a-zA-Z0-9-]+)/?$",
        TinylinkRedirectView.as_view(),
        name="tinylink_redirect",
    ),
]
