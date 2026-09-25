from django.urls import path

from web.views.friend.message.asr.consumer import ASRConsumer

websocket_urlpatterns = [
    path('ws/asr/', ASRConsumer.as_asgi()),
]
