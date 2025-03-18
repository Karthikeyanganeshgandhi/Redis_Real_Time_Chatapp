import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]
        self.username = self.user.first_name if self.user.is_authenticated else "Guest"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_content = data.get("message", "").strip()
            msg_type = data.get("type", "message")

            if msg_type == "typing":
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "typing", "username": self.username}
                )

            elif msg_type == "stop_typing":
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "stop_typing"}
                )

            elif msg_type == "delete":
                message_id = data.get("message_id")
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "delete", "message_id": message_id}
                )

            elif msg_type == "message" and message_content:
                # Save message in the database
                message_id = await self.save_message(self.room_name, self.user, message_content)

                # Send message to the group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "username": self.username,
                        "message": message_content,
                        "message_id": message_id,
                    }
                )
        except json.JSONDecodeError:
            print("❌ Invalid JSON received.")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "username": event["username"],
            "message": event["message"],
            "message_id": event["message_id"],
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({"type": "typing", "username": event["username"]}))

    async def stop_typing(self, event):
        await self.send(text_data=json.dumps({"type": "stop_typing"}))

    async def delete(self, event):
        await self.send(text_data=json.dumps({"type": "delete", "message_id": event["message_id"]}))

    @sync_to_async
    def save_message(self, room_name, user, message_content):
        """Save message to the database and return message ID."""
        room, _ = ChatRoom.objects.get_or_create(name=room_name)
        message = Message.objects.create(room=room, user=user, content=message_content)
        return message.id
