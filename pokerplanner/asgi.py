from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pokerplanner.token_authentication import TokenAuthMiddleware

from session.consumers import TestConsumer


ws_patterns = [
    path("session/<int:session_id>/", TestConsumer.as_asgi())
    # path("test/", TestConsumer.as_asgi())
]

application = ProtocolTypeRouter({
  "websocket": TokenAuthMiddleware(URLRouter(ws_patterns)),
  # "websocket": URLRouter(ws_patterns),
})
