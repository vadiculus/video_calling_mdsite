import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import PremiumChat, PremiumChatMessage, AdminChat, AdminChatMessage, OrderedCall
import json
from asgiref.sync import sync_to_async
import uuid
import pytz

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pk = self.scope["url_route"]["kwargs"]['call_id']
        self.room_name = f'call.{pk}'
        try:
            self.call = await database_sync_to_async(OrderedCall.objects.
                                                     select_related('visiting_time').
                                                     prefetch_related('participants').get)(pk=pk)
        except OrderedCall.DoesNotExist:
            return None

        self.user = self.scope['user']
        self.interlocutor = await sync_to_async(self.call.get_interlocutor)(self.user)

        await self.channel_layer.group_add(self.room_name, self.channel_name)

        if self.user in await sync_to_async(self.call.participants.all)():
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
            data['data'] = {'peer':self.user.username, 'full_name':self.user.full_name}
            await self.channel_layer.send(self.channel_name, {'type':'send_message', 'data':data})
        elif data['action'] == 'answer':
            await self.channel_layer.group_send(self.room_name, {'type':'send_message', 'data':data})
            if not self.call.call_start:
                await database_sync_to_async(self.call.set_call_start)(datetime.datetime.utcnow())
        elif data['action'] == 'end_call':
            await self.channel_layer.group_send(self.room_name, {'type': 'send_message', 'data': data})
        elif data['action'] == 'incoming_call':
            print('incoming_call')
            if not self.call.call_start:
                print('incoming_call')
                await self.channel_layer.group_send(f'standard.{self.interlocutor.username}',
                                                    {'type': 'send_new_message',
                                                     'data': {
                                                         'action': 'incoming_call',
                                                         'full_name': self.user.full_name,
                                                         'peer': self.user.username,
                                                         'time': str(self.call.visiting_time.time),
                                                         'call_id': str(self.call.id)
                                                     }
                                                     })
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
        self.interlocutor = await sync_to_async(self.chat.get_interlocutor)(self.user)
        if self.user in self.chat.participants.all():
            await self.channel_layer.group_add(self.chat_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.chat_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        data['peer'] = self.user.username
        data['full_name'] = self.user.full_name
        message = await sync_to_async(PremiumChatMessage.objects.create)(author=self.user, chat=self.chat,
                                                                       text=data['message'])
        data['time'] = str(message.time)
        data['id'] = message.id

        await self.channel_layer.group_send(f'standard.{self.interlocutor.username}',
                                            {'type': 'send_new_message', 'data': {'action':'new_premium_message',
                                                                                  'chat_id':str(self.chat.id)}})

        await self.channel_layer.group_send(self.chat_name, {'type': 'chat_message',
                                                             'data': data})

    async def chat_message(self, event):
        message = event['data']
        if self.user.username != message['peer']:
            try:
                message_obj = await database_sync_to_async(PremiumChatMessage.objects.get)(id=message['id'])
                message_obj.read = True
                await sync_to_async(message_obj.save)()
            except PremiumChatMessage.DoesNotExist:
                pass
        await self.send(text_data=json.dumps(message))

class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pk = self.scope["url_route"]["kwargs"]['chat_id']
        self.chat_name = f'admin_chat.{pk}'
        self.chat = await database_sync_to_async(AdminChat.objects.prefetch_related('participants').get)(pk=pk)
        self.user = self.scope['user']
        self.interlocutor = await sync_to_async(self.chat.get_interlocutor)(self.user)

        if self.user in self.chat.participants.all():
            await self.channel_layer.group_add(self.chat_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.chat_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        data['peer'] = self.user.username
        data['full_name'] = self.user.full_name
        message = await sync_to_async(AdminChatMessage.objects.create)(author=self.user, chat=self.chat, text=data['message'])

        data['time'] = str(message.time)
        data['id'] = message.id

        await self.channel_layer.group_send(f'standard.{self.interlocutor.username}',
                                            {'type': 'send_new_message', 'data': {'action': 'new_admin_message',
                                                                                  'chat_id': str(self.chat.id)}})

        await self.channel_layer.group_send(self.chat_name, {'type':'chat_message',
                                                             'data':data})

    async def chat_message(self, event):
        message = event['data']
        if self.user.username != message['peer']:
            message_obj = await database_sync_to_async(AdminChatMessage.objects.get)(id=message['id'])
            message_obj.read = True
            await sync_to_async(message_obj.save)()
        await self.send(text_data=json.dumps(message))

class MessagesConsumer(AsyncWebsocketConsumer):
    '''Для отображения что пользователю звонять и отображения нового сообщения'''
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = None
        if self.user.is_authenticated:
            self.group_name = f'standard.{self.user.username}'

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, code):
        self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data['action'] == 'get_peer_name':
            data['data'] = {'peer': self.user.username}
            await self.channel_layer.send(self.channel_name, {'type': 'send_new_message', 'data': data})
        else:
            self.channel_layer.group_send(self.group_name, {'type':'send_new_message', 'data':data})

    async def send_new_message(self, event):
        await self.send(text_data=json.dumps(event['data']))
