const chat_id = JSON.parse(document.querySelector('#chat_id').textContent);
let clientSocket = new WebSocket('ws://'+window.location.host+'/ws/admin_chat/'+chat_id+'/');
const messageInput = document.querySelector('#chat_message_input');
const send_btn = document.querySelector('#send_btn');
const chat_log = document.querySelector('#chat_log');

clientSocket.onopen = onOpen;
clientSocket.onclose = onClose;
clientSocket.onmessage = onMessage;

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

function onMessage(event){
    message_data = JSON.parse(event.data);
    let message_item = document.createElement('li');
    message_item.textContent = `${message_data.full_name}: ${message_data.message}`;
    let time = new Date(message_data.time);
    let hour = time.getHours() < 10 ? '0' + time.getHours() : time.getHours();
    let minute = time.getMinutes() < 10 ? '0' + time.getMinutes() : time.getMinutes();
    let time_element = document.createElement('span');
    time_element.innerHTML = `${hour}:${minute}`;
    message_item.append(document.createElement('br'));
    message_item.append(time_element);
    chat_log.append(message_item);
}

function onOpen(){
    console.log('OPENED');
}

function onClose(){
    console.log('CLOSED');
    connectionInterval = setInterval(()=>{
        if (clientSocket.readyState === WebSocket.CLOSED){
            clientSocket = new WebSocket('ws://'+window.location.host+'/ws/admin_chat/'+chat_id+'/');
            clientSocket.onopen = onOpen;
            clientSocket.onclose = onClose;
            clientSocket.onmessage = onMessage;
        } else {
            clearInterval(connectionInterval);
        }
    }, 5000);
}