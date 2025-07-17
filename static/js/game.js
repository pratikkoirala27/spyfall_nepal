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
                // Already handled by redirect in lobby
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
            item.innerHTML = `${player.name} - ${player.is_spy ? 'Spy' : player.role}`;
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
});