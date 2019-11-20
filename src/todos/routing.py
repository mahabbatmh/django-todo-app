from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'comments/(?P<todo_id>\w+)/$', consumers.CommentConsumer)
]
