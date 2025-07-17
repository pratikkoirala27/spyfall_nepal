import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameRoom, Player, GameMessage

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'game_{self.room_code}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'start_game':
            await self.start_game()
        elif message_type == 'player_joined':
            await self.notify_player_joined()

    async def handle_chat_message(self, data):
        player = await self.get_player(data['player_id'])
        if player:
            await self.save_message(player, data['message'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'player_name': player.name
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'player_name': event['player_name']
        }))

    async def start_game(self):
        room = await self.get_room()
        await database_sync_to_async(room.assign_roles)()
        players = await self.get_players(room)
        
        # Notify group that game has started
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_started',
                'location': room.location,
                'players': players,
                'spy_id': room.spy.id if room.spy else None
            }
        )

    async def game_started(self, event):
        # Send game start event to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'location': event['location'],
            'players': event['players'],
            'spy_id': event['spy_id']
        }))

    async def notify_player_joined(self):
        room = await self.get_room()
        players = await self.get_players(room)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_list',
                'players': players
            }
        )

    async def player_list(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_list',
            'players': event['players']
        }))

    @database_sync_to_async
    def get_room(self):
        return GameRoom.objects.get(code=self.room_code)
    
    @database_sync_to_async
    def get_player(self, player_id):
        try:
            return Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_message(self, player, message):
        GameMessage.objects.create(
            room=player.room,
            player=player,
            content=message
        )
    
    @database_sync_to_async
    def get_players(self, room):
        players = list(Player.objects.filter(room=room).values('id', 'name', 'is_spy', 'role'))
        return players