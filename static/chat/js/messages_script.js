let messagesSocket = new WebSocket(`ws://${window.location.host}/chat/ws/messages/`);
let peer;

messagesSocket.onopen = onOpen;
messagesSocket.onclose = onClose;
messagesSocket.onmessage = onMessage;

function onMessage(event){
    message = JSON.parse(event['data']);

    console.log(message);
    
    switch (message.action){
        case 'get_peer_name':
            peer = message.data.peer;
            break;
        case 'new_premium_message':
            let new_premium_messages = document.querySelector('#new_premium_messages');
            try{
                if(!(message.chat_id == chat_id)){
                    new_premium_messages.innerHTML = parseInt(new_premium_messages.innerHTML) ? parseInt(new_premium_messages.innerHTML) + 1 : 1;
                }
            } catch (error){
                new_premium_messages.innerHTML = parseInt(new_premium_messages.innerHTML) ? parseInt(new_premium_messages.innerHTML) + 1 : 1;
            }
            let chat_item = document.querySelector(`.new_messages_coint, [data-chat-id = "${message.chat_id}"]`);
            if (chat_item){
                chat_item.innerHTML =  parseInt(chat_item.innerHTML) + 1;
            }
            break;
        case 'new_admin_message':
            let new_admin_messages = document.querySelector('#new_admin_messages');
            try{
                if(!(message.chat_id == chat_id)){
                    new_admin_messages.innerHTML = parseInt(new_admin_messages.innerHTML) ? parseInt(new_admin_messages.innerHTML) + 1 : 1;
                }
            } catch (error){
                new_admin_messages.innerHTML = parseInt(new_admin_messages.innerHTML) ? parseInt(new_admin_messages.innerHTML) + 1 : 1;
            }
            let admin_chat_item = document.querySelector(`.new_messages_coint, [data-chat-id = "${message.chat_id}"]`);
            if (admin_chat_item){
                admin_chat_item.innerHTML =  parseInt(admin_chat_item.innerHTML) + 1;
            }
            break;
        case 'incoming_call':
            console.log('INCOMING_MESSAGE');
            let incoming_call_window = document.querySelector('#incoming_call_window');
            let user_full_name = document.querySelector('#call__user_full_name');
            let call_start_btn = document.querySelector('#call__call_start_btn');
            call_start_btn.href = `http://${window.location.host}/chat/ordered-call/${message.call_id}`;
            let call_time = document.querySelector('#call__time');
            let time = new Date(message.time); 
            let hour = time.getHours() < 10 ? '0' + time.getHours() : time.getHours();
            let minute = time.getMinutes() < 10 ? '0' + time.getMinutes() : time.getMinutes();
            call_time.innerHTML = `Забронированый звонок на ${hour}:${minute}` 
            user_full_name.innerHTML = message.full_name;
            incoming_call_window.style.display = 'block';
            break;
    }
};

function getPeerName(){
    send({
        action:'get_peer_name'
    });
    console.log('get_peer_name');
}

function onOpen(){
    console.log('OPENED');
    getPeerName();
}

function onClose(){
    console.log('CLOSED');
    connectionInterval = setInterval(()=>{
        if (messagesSocket.readyState === WebSocket.CLOSED){
            messagesSocket = new WebSocket(`ws://${window.location.host}/chat/ws/messages/`);
            messagesSocket.onopen = onOpen;
            messagesSocket.onclose = onClose;
            messagesSocket.onmessage = onMessage;
        } else {
            clearInterval(connectionInterval);
        }
    }, 5000);
}

function send(data){
    messagesSocket.send(JSON.stringify(data));
}

// function incoming_call_ajax(username){
//     const xhr = new XMLHttpRequest();
//     let data = {};
//     xhr.open('GET', `http://${window.location.host}/accounts/get-user-photo/${username}/`);
//     xhr.setRequestHeader('Content-Type', 'application/json');
//     xhr.setRequestHeader('X-CSRFToken', csrftoken);
//     xhr.setRequestHeader('x-requested-with', 'XMLHttpRequest');

document.querySelector('#call__cansel_call_btn').addEventListener('click', ()=>{
    let incoming_call_window = document.querySelector('#incoming_call_window');
    incoming_call_window.style.display = 'none';
});
