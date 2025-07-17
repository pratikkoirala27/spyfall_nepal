from django.shortcuts import render, redirect
from .models import GameRoom, Player
import random
import string

def home(request):
    return render(request, 'game/home.html')

def create_room(request):
    if request.method == 'POST':
        # Generate a unique room code
        while True:
            room_code = ''.join(random.choices(string.ascii_uppercase, k=6))
            if not GameRoom.objects.filter(code=room_code).exists():
                break
        room = GameRoom.objects.create(code=room_code)
        return redirect('lobby', room_code=room.code)
    return redirect('home')

def join_room(request):
    if request.method == 'POST':
        room_code = request.POST.get('room_code').upper()
        try:
            room = GameRoom.objects.get(code=room_code)
            return redirect('lobby', room_code=room.code)
        except GameRoom.DoesNotExist:
            return redirect('home')
    return redirect('home')

def lobby(request, room_code):
    try:
        room = GameRoom.objects.get(code=room_code)
    except GameRoom.DoesNotExist:
        return redirect('home')
    
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    # Check if player already exists in the room for this session
    if not Player.objects.filter(room=room, session_id=session_key).exists():
        player_name = f"Player-{random.randint(1000,9999)}"
        Player.objects.create(
            session_id=session_key,
            name=player_name,
            room=room
        )
    
    players = Player.objects.filter(room=room)
    return render(request, 'game/lobby.html', {
        'room_code': room_code,
        'players': players
    })

def game_room(request, room_code):
    try:
        room = GameRoom.objects.get(code=room_code)
    except GameRoom.DoesNotExist:
        return redirect('home')
    
    session_key = request.session.session_key
    if not session_key:
        return redirect('home')
    
    try:
        player = Player.objects.get(room=room, session_id=session_key)
    except Player.DoesNotExist:
        return redirect('lobby', room_code=room_code)
    
    return render(request, 'game/game_room.html', {
        'room_code': room_code,
        'player': player,
        'is_spy': player.is_spy,
        'role': player.role
    })