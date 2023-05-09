import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import PremiumChat, PremiumChatMessage, AdminChat, AdminChatMessage, OrderedCall
import json
from asgiref.sync import sync_to_async
import uuid

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pk = self.scope["url_route"]["kwargs"]['call_id']
        self.room_name = f'call.{pk}'
        self.chat = await database_sync_to_async(OrderedCall.objects.prefetch_related('participants').get)(pk=pk)
        self.user = self.scope['user']
        self.channel_id = str(uuid.uuid4()) #Индитификатор dataChannel для нормального переподключения

        await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.channel_layer.group_send(self.room_name, {'type': 'send_message',
                                                             'data': {
                                                                 'peer': self.user.username,
                                                                 'action': 'connected'}})
        if self.user in await sync_to_async(self.chat.participants.all)():
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_send(self.room_name, {'type':'send_message',
                                                              'data':{
                                                                  'peer':self.user.username,
                                                                  'action':'disconnected'}})
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        data['peer'] = self.user.username

        if data['action'] == 'get_peer_name':
            data['data'] = {'peer':self.user.username, 'full_name':self.user.full_name, 'channel_id':self.channel_id}
            await self.channel_layer.send(self.channel_name, {'type':'send_message', 'data':data})
        elif data['action'] == 'offer':
            data['new_channel_id'] = self.channel_id
            await self.channel_layer.group_send(self.room_name, {'type':'send_message', 'data':data})
        elif data['action'] == 'answer':
            await self.channel_layer.group_send(self.room_name, {'type':'send_message', 'data':data})
            self.chat.call_start = datetime.datetime.now()
            await database_sync_to_async(self.chat.save)()
            print('answer')
        else:
            await self.channel_layer.group_send(self.room_name, {'type':'send_message', 'data':data})

    async def send_message(self, event):
        data = json.dumps(event['data'])

        await self.send(data)


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

