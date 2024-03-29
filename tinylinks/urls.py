"""URLs for the ``django-tinylinks`` app."""
from django.conf import settings
from django.conf.urls import include
from django.urls import re_path
from django.views.generic import RedirectView, TemplateView
from tinylinks.router import CustomDefaultRouter
from tinylinks.views import (ShorterURL, StatisticsView, TinylinkCreateView,
                             TinylinkDeleteView, TinylinkListView,
                             TinylinkRedirectView, TinylinkUpdateView,
                             TinylinkViewSet, UserViewSet, db_stats, stats,
                             tinylink_expand, tinylink_stats)

# Create router and register our API viewsets with it.
router = CustomDefaultRouter()
router.register(
    r"{}".format(getattr(settings, "TINYLINK_API_PREFIX", "tinylinks")), TinylinkViewSet
)
router.register(r"users", UserViewSet)

PREFIX = getattr(settings, "TINYLINK_SHORT_URL_PREFIX", "")

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
    re_path(r"^yourls-api.php", ShorterURL.as_view(), name="shorter_url",),
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
        r"^{}{}".format(
            PREFIX + "/" if PREFIX else "", "(?P<short_url>[a-zA-Z0-9-]+)$"
        ),
        TinylinkRedirectView.as_view(),
        name="tinylink_redirect",
    ),
]
