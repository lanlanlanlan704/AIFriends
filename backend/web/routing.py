from django.urls import path

from web.views.friend.message.asr.consumer import ASRConsumer
from web.views.friend.message.proactive.consumer import ProactiveConsumer

websocket_urlpatterns = [
    path('ws/asr/', ASRConsumer.as_asgi()),
    path('ws/proactive/', ProactiveConsumer.as_asgi()),
]
