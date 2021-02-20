from rest_framework.routers import DefaultRouter

from tinylinks.views import CustomDefaultRouterAPIView


class CustomDefaultRouter(DefaultRouter):
    APIRootView = CustomDefaultRouterAPIView
