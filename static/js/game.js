document.addEventListener('DOMContentLoaded', function() {
    const roomCode = window.location.pathname.split('/')[2];
    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${roomCode}/`);
    
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        switch(data.type) {
            case 'chat':
                addMessageToChat(data.player_name, data.message);
                break;
            case 'player_list':
                updatePlayerList(data.players);
                break;
            case 'game_started':
                // Update location for non-spy players
                if (!document.getElementById('player-is-spy').value) {
                    document.getElementById('location').textContent = data.location;
                }
                updatePlayerList(data.players);
                break;
        }
    };
    
    function addMessageToChat(player, message) {
        const chatBox = document.getElementById('chat-box');
        const messageElement = document.createElement('div');
        messageElement.className = 'mb-2';
        messageElement.innerHTML = `<strong>${player}:</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    function updatePlayerList(players) {
        const playerList = document.getElementById('player-list');
        playerList.innerHTML = '';
        players.forEach(player => {
            const item = document.createElement('li');
            item.className = 'list-group-item';
            if (player.is_spy) {
                item.innerHTML = `${player.name} - <span class="text-danger">Spy</span>`;
            } else {
                item.innerHTML = `${player.name} - ${player.role}`;
            }
            playerList.appendChild(item);
        });
    }
    
    document.getElementById('chat-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        if (message) {
            socket.send(JSON.stringify({
                type: 'chat_message',
                player_id: document.getElementById('player-id').value,
                message: message
            }));
            messageInput.value = '';
        }
    });
    
    // Request initial player list
    socket.onopen = function() {
        socket.send(JSON.stringify({
            type: 'player_joined'
        }));
    };
});