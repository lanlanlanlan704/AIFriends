import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# 第一步：先把 Django 的 HTTP 应用造出来，这一步会完成 Django 的全部初始化
django_asgi_app = get_asgi_application()

# 第二步：下面这些 import 必须写在上面那行之后
from channels.routing import ProtocolTypeRouter, URLRouter

from web.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # 普通 HTTP 请求：还是交给 Django 原来那一套，行为完全不变
    "http": django_asgi_app,
    # WebSocket 请求：走我们新写的路由表
    "websocket": URLRouter(websocket_urlpatterns),
})
