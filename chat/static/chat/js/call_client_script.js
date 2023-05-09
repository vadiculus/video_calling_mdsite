const call_id = JSON.parse(document.querySelector('#call_id').textContent);
const clientSocket = new WebSocket(`ws://${window.location.host}/ws/ordered_call/${call_id}/`);
let localVideo = document.getElementById('local-video');
let remoteVideo = document.getElementById('remote-video');
let peerConnection;
let peer;
let full_name;
let localStream;
let remoteStream;
let dataChannel;
let videoTrack;
let initializeChannelId;
const csrftoken = getCookie('csrftoken');

const config = {
    iceServers: [
        {
            urls: "stun:stun.l.google.com:19302"
        },
    ]
}

const constraints = {
    audio: true,
    video: true
}

function getCookie(name){
    let cookieValue = null;
    if (document.cookie && document.cookie != ''){
        const cookies = document.cookie.split(';');
        for(const i = 0; i<cookies.length; i++){
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length+1) ===(name + "=")){
                cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                break;
            }
        }
    }
    return cookieValue;
}

clientSocket.addEventListener('message', (event)=>{
    message = JSON.parse(event['data']);

    console.log(message);

    if (message.peer === peer){
        return;
    }

    console.log(message);
    
    switch (message.action){
        case 'offer':
            handlerOffer(message.data, message.new_channel_id);
            document.querySelector('#connection_state').style.display = 'none';
        case 'candidate':
            handlerCandidate(message.data)
            break;
        case 'answer':
            handlerAnswer(message.data)
            break;
        case 'get_peer_name':
            peer = message.data.peer;
            full_name = message.data.full_name;
            initializeChannelId = message.channel_id;
            initialize();
            break;
        case 'disconnected':
            remoteVideo.srcObject = null;
            console.log('Disconnected!')
            document.querySelector('#connection_state').style.display = 'block';
            document.querySelector('#interlocutor_microphone_state').style.visibility = 'hidden'
            dataChannel.close();
            break;
        case 'connected':
            console.log('Connected!')
            document.querySelector('#connection_state').style.display = 'none';
            break;
    }
});

function getPeerName(){
    send({
        action:'get_peer_name'
    });
}

clientSocket.onopen = function(){
    console.log('Connected');
    getPeerName();
}


function send(message){
    clientSocket.send(JSON.stringify(message));
}

function initialize(){
    peerConnection = new RTCPeerConnection(config);

    peerConnection.onicecandidate = function(event){
        if (event.candidate){
            send({
                action: "candidate",
                data: event.candidate
            })
        }
    }

    createDataChannel();

    peerConnection.ondatachannel = function(event){
        console.log('create dataChannel');
        dataChannel = event.channel;
    }

    peerConnection.ontrack = function(event){
        const reStream = event.streams[0]
        reStream.getVideoTracks()[0].onended = (event)=>{
            remoteVideo.style.visibility = 'hidden'
        } 
        remoteVideo.srcObject = reStream;
    }

    navigator.getUserMedia(constraints, function (thisStream) { 
        localStream = thisStream;

        peerConnection.addStream(localStream);

        peerConnection.createOffer(function(offer){
        
            peerConnection.setLocalDescription(offer)
    
            send({
                action: 'offer',
                data: offer,
            });
    
        }, function(error){
            console.log('createOffer error:', error)});

        localVideo.srcObject = localStream;
    
    }, function (err) {
        console.log('error: ', error)
    }); 
}

function handlerOffer(offer, channel_id){
    try{
        dataChannel.close();
    }
    catch (error){
        console.log(error);
    }
    createDataChannel(channel_id=channel_id);
    peerConnection.setRemoteDescription(offer)
        .then(() => {
            console.log('Set Remote Description', peer);
            return peerConnection.createAnswer()
        })
        .then(answer => {
            console.log('Answer create');
            peerConnection.setLocalDescription(answer).then(createDataChannel);

            send({
                action: "answer",
                data: answer
            })
        });
}

function handlerAnswer(answer){
    peerConnection.setRemoteDescription(new RTCSessionDescription(answer)).then(()=>console.log(peerConnection.remoteDescription));
}

function handlerCandidate(candidate){
    peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
}

document.querySelector('#audio-checkbox').addEventListener('change',(event)=>{
    if (dataChannel.readyState === 'open'){
        console.log('open');
        dataChannel.send(JSON.stringify({   
            full_name,
            action: 'change_audio',
            data: event.target.checked,
        }))
        audio = localStream.getAudioTracks()[0].enabled = event.target.checked;
        if (event.target.checked){
            document.querySelector('#my_microphone_state').style.visibility = 'hidden';
        } else {
            document.querySelector('#my_microphone_state').style.visibility = 'visible';
        }
    } else {
        event.target.checked = true;event.target.checked = true;
    }
})

document.querySelector('#video-checkbox').addEventListener('change', (event)=>{
    if (dataChannel.readyState === 'open'){
        dataChannel.send(JSON.stringify({
            full_name,
            action: 'change_camera',
            data: event.target.checked,
        }))
        video = localStream.getVideoTracks()[0].enabled = event.target.checked;
        if (event.target.checked){
            localVideo.style.visibility = 'visible'
        } else {
            localVideo.style.visibility = 'hidden'
        }
    } else {
        event.target.checked = true;
    }
})

document.querySelector('#send-msg-button').addEventListener('click', ()=>{
    let message = document.querySelector('#chat-input');
    if (dataChannel.readyState === 'open'){
        console.log(message.value)
        dataChannel.send(JSON.stringify({
            full_name,
            action: 'message',
            message: message.value,
        }));
        let chat_log = document.querySelector('#chat-log');
        let message_item = document.createElement('li');
        message_item.textContent = `${full_name}: ${message.value}`;
        chat_log.append(message_item);
        message.value = '';
    }    
})

document.querySelector('#chat-input').addEventListener('keydown', (event)=>{
    if (event.keyCode === 13){
        document.querySelector('#send-msg-button').click();
    }
})

function createDataChannel(channel_id=null){
    console.log(channel_id);
    if(channel_id){
        console.log('NEW CHANNELID!!!');
        dataChannel = peerConnection.createDataChannel(channel_id, {
            reliable: true
        })
    } else {
        dataChannel = peerConnection.createDataChannel(initializeChannelId, {
            reliable: true
        })
    }
    

    dataChannel.onopen = function(){
        console.log('dataChannel opened');
        remoteVideo.style.visibility = 'visible';
        document.querySelector('#connection_state').style.display = 'none';
    }

    dataChannel.obclose = function(){
        console.log('dataChannel closed');
        remoteVideo.srcObject = null;
    }

    dataChannel.onmessage = (event)=>{
        data = JSON.parse(event.data)
        switch (data.action){
            case 'change_camera':
                console.log('change_camera');
                if (data.data){
                    remoteVideo.style.visibility = 'visible'
                } else {
                    remoteVideo.style.visibility = 'hidden'
                }
                break;

            case 'change_audio':
                let audio_state = document.querySelector('#interlocutor_microphone_state');
                if (data.data){
                    audio_state.style.visibility = 'hidden'
                } else {
                    audio_state.style.visibility = 'visible'
                }
                break;

            case 'message':
                let chat_log = document.querySelector('#chat-log');
                let message_item = document.createElement('li');
                message_item.textContent = `${data.full_name}: ${data.message}`;
                chat_log.append(message_item);
                break;
        }
    }
}

function send_call_ending_status(status){
    console.log(`http://${window.location.host}/chat/end-call/${call_id}/`);
    const xhr = new XMLHttpRequest();
    let data;
    xhr.open('POST', `http://${window.location.host}/chat/end-call/${call_id}/`);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    switch (status){
        case 'complaint':
            data = new FormData(document.querySelector('#complaint_form'));
            break;
        case 'review':
            data = new FormData(document.querySelector('#complaint_form'));
            break;
        case 'success':
            data = 'status=success'
            break;
    }
    xhr.onload = function(event){
        if (xhr.status !== 201){
            return;
        }
        let response = JSON.parse(xhr.response);
        console.log(response);
        if (response.status === 'success'){
            document.body.style.background = 'red';
        }
    }
    xhr.send(data);
}

document.querySelector('#end_call_btn').addEventListener('click', send_call_ending_status('success'));

document.querySelector('#review_btn').addEventListener('click', send_call_ending_status('review'));

document.querySelector('complaint_btn').addEventListener('click', send_call_ending_status('review'));