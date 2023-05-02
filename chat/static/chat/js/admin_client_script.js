window.addEventListener('DOMContentLoaded', ()=>{
    const chat_id = JSON.parse(document.querySelector('#chat_id').textContent);
    const clientSocket = new WebSocket('ws://'+window.location.host+'/ws/admin_chat/'+chat_id+'/');
    const messageInput = document.querySelector('#chat_message_input');
    const send_btn = document.querySelector('#send_btn');
    const chat_log = document.querySelector('#chat_log');

    messageInput.addEventListener('keydown', (event)=>{
        if (event.keyCode == 13){
            send_btn.click()
        }
    });

    send_btn.addEventListener('click', ()=>{
        let message_value = document.querySelector('#chat_message_input').value;
        messageInput.value = '';
        clientSocket.send(JSON.stringify({message:message_value}));
    });

    clientSocket.onopen = function(event){
        console.log('Connected');
    }

    clientSocket.onclose = function(event){
        console.log('Closed');
    }

    clientSocket.onmessage = function(event){
        message_data = JSON.parse(event.data).message;
        let message_item = document.createElement('li');
        message_item.textContent = `${message_data.author}: ${message_data.message}`;
        chat_log.append(message_item);

        console.log(message_data.message);
    }
})