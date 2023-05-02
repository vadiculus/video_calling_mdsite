from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import PremiumChat, PremiumChatMessage, AdminChat, AdminChatMessage
import json
from asgiref.sync import sync_to_async

class PremiumConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pk = self.scope["url_route"]["kwargs"]['chat_id']
        self.chat_name = f'premium_chat.{pk}'
        self.chat = await database_sync_to_async(PremiumChat.objects.prefetch_related('participants').get)(pk=pk)
        self.user = self.scope['user']

        if self.user in self.chat.participants.all():
            await self.channel_layer.group_add(self.chat_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.chat_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message_data = data['message']
        await sync_to_async(PremiumChatMessage.objects.create)\
            (author=self.user, chat=self.chat, text=message_data)

        await self.channel_layer.group_send(self.chat_name, {'type':'chat_message',
                                                             'data':{'author':self.user.full_name,
                                                                     'message':message_data}})

    async def chat_message(self, event):
        message = event['data']
        await self.send(text_data=json.dumps({'message':message}))

class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pk = self.scope["url_route"]["kwargs"]['chat_id']
        self.chat_name = f'admin_chat.{pk}'
        self.chat = await database_sync_to_async(AdminChat.objects.prefetch_related('participants').get)(pk=pk)
        self.user = self.scope['user']

        if self.user in self.chat.participants.all():
            await self.channel_layer.group_add(self.chat_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.chat_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message_data = data['message']
        author = ''
        await sync_to_async(AdminChatMessage.objects.create)(author=self.user, chat=self.chat, text=message_data)

        await self.channel_layer.group_send(self.chat_name, {'type':'chat_message',
                                                             'data':{'author':self.user.full_name,
                                                                     'message':message_data}})

    async def chat_message(self, event):
        message = event['data']
        await self.send(text_data=json.dumps({'message':message}))

