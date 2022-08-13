"""Routing"""
from django.urls import re_path

from cstor.dashboard.cloud import consumers


ws_urlpatterns = [
    re_path(r"ws/(?P<token>\w+)/$", consumers.CloudConsumer.as_asgi()),
]
