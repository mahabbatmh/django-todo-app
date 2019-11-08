from channels.routing import route
from .consumers import *

channel_routing = [
    route('websocket.connect', ws_add, path=r'^/comments/(?P<id>[0-9]{4})$'),
    route('websocket.receive', ws_message, path=r'^/comments/(?P<id>[0-9]{4})$'),
    route('websocket.disconnect', ws_disconnect, path=r'^/comments/(?P<id>[0-9]{4})$'),
]
