from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.gis.geoip import GeoIP

from tinylinks.piwik import parse_cookie
from tinylinks.models import TinylinkLog
import json
import random
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
import urllib.request, urllib.error, urllib.parse

CURRENT_DOMAIN = Site.objects.get_current().domain
TRACK_OFFSET = 50

if settings.GEOIP_PATH:
    G = GeoIP()
else:
    country = ''


class Command(BaseCommand):
    def track_to_piwik(self, views):
        visits = []
        for view in views:
            url = view.tinylink
            params = parse_cookie(view.cookie)
            address = 'http://%s/%s' % (CURRENT_DOMAIN, url.short_url)
            if settings.GEOIP_PATH:
                country = G.country(view.remote_ip).get('country_code').lower()
            params.update({'rand': random.randint(0, 1000000), 'url': address, 'urlref': view.referrer,
                           'ua': view.user_agent.encode('utf-8'), 'cip': view.remote_ip,
                           'cdt': view.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                           'country': country, 'new_visit': 1,
                           'idsite': settings.PIWIK_ID, 'rec': 1, 'token_auth': settings.PIWIK_TOKEN,
                           'action_name': url.long_url.encode('utf-8'), 'apiv': 1})

            res = '?' + urlencode(params)
            visits.append(res)
        payload = {'requests': visits, 'token_auth': settings.PIWIK_TOKEN}
        #print payload
        req = urllib.request.Request(settings.PIWIK_URL)
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req, json.dumps(payload))
        print(('Another %d views tracked well!' % TRACK_OFFSET))
        TinylinkLog.objects.filter(pk__in=views).update(tracked=True)

    def handle(self, *args, **options):
        num_visits = TinylinkLog.objects.filter(tracked=False).count()
        print(('Untracked views: %d' % num_visits))
        if num_visits == 0:
            return

        views = TinylinkLog.objects.filter(tracked=False).prefetch_related('tinylink')
        views_count = views.count()
        if views_count < TRACK_OFFSET:
            self.track_to_piwik(views)
        else:
            i = 0
            while views_count > i:
                self.track_to_piwik(views[i:i + TRACK_OFFSET])
                i += TRACK_OFFSET
