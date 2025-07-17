from django.db import models
import json
import random

class GameRoom(models.Model):
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    game_started = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True, null=True)
    spy = models.ForeignKey('Player', null=True, blank=True, on_delete=models.SET_NULL, related_name='spy_in_room')

    def assign_roles(self):
        with open('locations.json') as f:
            locations_data = json.load(f)
        
        locations = list(locations_data['locations'].keys())
        chosen_location = random.choice(locations)
        self.location = chosen_location
        self.save()
        
        players = list(self.player_set.all())
        random.shuffle(players)
        
        # Assign spy
        spy = players[0]
        spy.is_spy = True
        spy.role = "Spy"
        spy.save()
        self.spy = spy
        self.save()
        
        # Assign roles to others
        roles = locations_data['locations'][chosen_location]['people_types']
        for i, player in enumerate(players[1:]):
            player.role = roles[i % len(roles)]
            player.save()

class Player(models.Model):
    session_id = models.CharField(max_length=255)
    name = models.CharField(max_length=50)
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    is_spy = models.BooleanField(default=False)
    role = models.CharField(max_length=100, blank=True)

class GameMessage(models.Model):
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)