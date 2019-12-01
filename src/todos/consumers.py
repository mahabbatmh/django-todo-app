from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from django.core.exceptions import ObjectDoesNotExist

from .models import Comment, TodoUser, PermissionEnum
from django.core import serializers

from django.contrib.auth.models import User


class CommentConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = self.scope['url_route']['kwargs']['todo_id']
        self.room_group_name = 'comments_%s' % self.room_name

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        session_user = User.objects.get(username=self.scope['user'])
        try:
            todo_user = TodoUser.objects.get(todo_id=self.room_name, user=session_user,
                                             permission__in=(PermissionEnum.COMMENT.value, PermissionEnum.EDIT.value))
        except ObjectDoesNotExist:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'comment_message',
                    'message': 'ACCESS_DENIED'
                }
            )

        new_comment = Comment(todo_id=self.room_name, user=session_user, message=message)
        new_comment.save()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'comment_message',
                'message': {
                    "user_id": session_user.id,
                    "user_email": session_user.email,
                    "message": message,
                    "comment_id": new_comment.id
                }
            }
        )

    def comment_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
