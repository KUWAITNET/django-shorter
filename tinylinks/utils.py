from rest_framework.routers import DefaultRouter

from .forms import TinylinkForm
from .views import CustomDefaultRouterAPIView


def shortify_url(url):
    data = {'data': {'long_url': url}, 'mode': None}
    form = TinylinkForm(**data)
    if form.is_valid():
        obj = form.save()
        return obj.short_url
    else:
        return url

class CustomDefaultRouter(DefaultRouter):
    APIRootView = CustomDefaultRouterAPIView
