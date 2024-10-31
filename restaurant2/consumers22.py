
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class RestaurantOrdersConsumer(WebsocketConsumer):
    def connect(self):
        self.restaurant_id = self.scope['url_route']['kwargs']['restaurant_id']
        self.room_group_name = f'restaurant_{self.restaurant_id}_orders'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # Handle incoming messages if needed (not typically used for broadcasts)
        pass

    def send_notification(self, event):
        # Send notification to WebSocket
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
