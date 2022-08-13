"""Consumers for Channels"""
import json
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class CloudConsumer(WebsocketConsumer):
    """Cloud Consumer for ws/$

    self.scope["path"] - path of the http request
    self.scope["headers"] - header sent
    self.scope["method"] - method name of the http request
    self.scope["user"] - User object
    self.scope["url_route"] - captured groups from URL
    """
    def connect(self):
        """Connect Handler"""
        if not isinstance(self.scope["user"], AnonymousUser):
            self.user = self.scope["user"]
            # Join a channel for this user_id
            self.user_channel: str = f"user_{self.user.id}"
            async_to_sync(self.channel_layer.group_add)(
                self.user_channel,
                self.channel_name,
            )

            self.accept()


    def disconnect(self, close_code):
        """Close Handler"""
        # Leave the group
        print(f"Leaving channel: {self.user_channel}")
        async_to_sync(self.channel_layer.group_discard)(
            self.user_channel,
            self.channel_name,
        )

    def receive(self, text_data: str):
        """Receive a websocket message from client"""
        socket_data: dict = json.loads(text_data)
        print(f"Received: {socket_data}")


        # Echo back the message sent
        self.send(text_data=json.dumps({
            "message": socket_data.get("message"),
        }))


    def notify_user(self, evt):
        """NotifyUser on client"""
        data: dict = evt["data"]
        text_data: str = json.dumps(data)
        self.send(text_data=text_data)
