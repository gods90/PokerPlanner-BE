from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from pokerplanner.token_authentication import TokenAuthMiddleware

from session.consumers import SessionConsumer


ws_patterns = [
    path("session/<int:session_id>/", SessionConsumer.as_asgi())
]

application = ProtocolTypeRouter({
  "websocket": TokenAuthMiddleware(URLRouter(ws_patterns)),
})
