const call_id = JSON.parse(document.querySelector('#call_id').textContent);
let clientSocket = new WebSocket(`ws://${window.location.host}/ws/ordered_call/${call_id}/`);
let localVideo = document.getElementById('local-video');
let remoteVideo = document.getElementById('remote-video');
let peerConnection;
let peer;
let full_name;
let localStream;
let remoteStream;
let videoTrack;
const endTimeStr = JSON.parse(document.querySelector('#call_end_time').textContent);
const endTime = new Date(endTimeStr);
const csrftoken = getCookie('csrftoken');
let timer;
let connectionInterval;

clientSocket.onopen = onOpen;
clientSocket.onclose = onClose;
clientSocket.onmessage = onMessage;

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
            if (cookie.substring(0, name.length+1) === (name + "=")){
                cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                break;
            }
        }
    }
    return cookieValue;
}

function end_call(){
    document.querySelector('#call_interface_container').style.display = 'none';
    document.querySelector('#end_call_question').style.display = 'none';
    document.querySelector('#call_end_info').style.display = 'block';
    send_call_ending_status('success');
    send({
        action: 'call_end',
    })
    peerConnection.close();
    clientSocket.close();
    document.getElementById('connection_info').remove();
}

function Timer(){
    if (new Date() > endTime){
        clearInterval(timer);
        end_call();
    } else {
        let date = new Date();
        let timestamp = Math.floor((endTime - date) / 1000);
        let hours = Math.floor(timestamp / 60 / 60) < 10 ? `0${Math.floor(timestamp / 60 / 60)}`: Math.floor(timestamp / 60 / 60); 
        let minutes = Math.floor(timestamp / 60) - (hours * 60) < 10 ? `0${Math.floor(timestamp / 60) - (hours * 60)}`: Math.floor(timestamp / 60) - (hours * 60);
        let seconds = timestamp % 60 < 10 ? `0${timestamp % 60}`: timestamp % 60 ;
        document.querySelector('#timer').innerHTML = 'Время до конца: ' + hours + ':' + minutes + ':' + seconds; 
    }
}

timer = setInterval(Timer, 1000);

function onMessage(event){
    message = JSON.parse(event['data']);

    if (message.peer === peer || (!peer && message.action != 'get_peer_name')){
        return;
    }

    console.log(message);
    
    switch (message.action){
        case 'offer':
            handlerOffer(message.data);
            document.querySelector('#connection_state').style.display = 'none';
        case 'candidate':
            handlerCandidate(message.data);
            break;
        case 'answer':
            handlerAnswer(message.data);
            break;
        case 'get_peer_name':
            peer = message.data.peer;
            full_name = message.data.full_name;
            initialize(first_time=true);
            send({
                action:'incoming_call'
            });
            // setTimeout(()=>initialize(), 3000);
            break;
        case 'disconnected':
            remoteVideo.srcObject = null;
            console.log('Disconnected!');
            document.querySelector('#connection_state').style.display = 'block';
            document.querySelector('#interlocutor_microphone_state').style.visibility = 'hidden'
            break;
        case 'connected':
            console.log('Connected!')
            document.querySelector('#connection_state').style.display = 'none';
            if (message.data){
                document.querySelector('#interlocutor_microphone_state').style.visibility = 'hidden'
            } else {
                document.querySelector('#interlocutor_microphone_state').style.visibility = 'visible'
            }

            if (message.data){
                remoteVideo.style.visibility = 'visible'
            } else {
                remoteVideo.style.visibility = 'hidden'
            }

            send({
                action: 'media_info',
                video: document.querySelector('#video-checkbox').checked,
                audio: document.querySelector('#audio-checkbox').checked,
            })

            break;
        case 'message':
            let chat_log = document.querySelector('#chat-log');
            let message_item = document.createElement('li');
            message_item.textContent = `${message.full_name}: ${message.message}`;
            chat_log.append(message_item);
            break;
        case 'change_camera':
            if (message.data){
                remoteVideo.style.visibility = 'visible'
            } else {
                remoteVideo.style.visibility = 'hidden'
            }
            break;

        case 'change_audio':
            let audio_state = document.querySelector('#interlocutor_microphone_state');
            if (message.data){
                audio_state.style.visibility = 'hidden'
            } else {
                audio_state.style.visibility = 'visible'
            }
            break;

        case 'end_call':
            end_call();
            break;
            
        case 'complaint':
            window.location.href = `http://${window.location.host}/moderation/complaint-info/accused/`;
            break;
        case 'media_info':
            if (message.audio){
                document.querySelector('#interlocutor_microphone_state').style.visibility = 'hidden'
            } else {
                document.querySelector('#interlocutor_microphone_state').style.visibility = 'visible'
            }

            if (message.video){
                remoteVideo.style.visibility = 'visible'
            } else {
                remoteVideo.style.visibility = 'hidden'
            }
            break;
    }
};

function getPeerName(){
    send({
        action:'get_peer_name'
    });
}

function onOpen(){
    console.log('OPENED');
    document.querySelector('#connection_info').style.display = 'none';
    send({
        action: 'connected',
        data: {
            video: document.querySelector('#video-checkbox').checked,
            audio: document.querySelector('#audio-checkbox').checked,
        }
    })
    if (peer){
        initialize();
    } else {
        getPeerName();
    }
}

function onClose(){
    console.log('CLOSED');
    document.querySelector('#connection_info').style.display = 'block';
    connectionInterval = setInterval(()=>{
        if (clientSocket.readyState === WebSocket.CLOSED){
            peerConnection = null;
            clientSocket = new WebSocket(`ws://${window.location.host}/ws/ordered_call/${call_id}/`);
            clientSocket.onopen = onOpen;
            clientSocket.onclose = onClose;
            clientSocket.onmessage = onMessage;
        } else {
            clearInterval(connectionInterval);
        }
    }, 10000);
    peer = null;
    peerConnection.close();
}


function send(message){
    clientSocket.send(JSON.stringify(message));
}

function initialize(first_time=false){
    peerConnection = new RTCPeerConnection(config);

    peerConnection.onsignalingstatechange = function(){
        console.log('sigenalingStage: ',peerConnection.signalingState);
    }

    peerConnection.oniceconnectionstatechange = function(){
        console.log('iceConnectionState: ',peerConnection.iceConnectionState);
    }

    peerConnection.onreadystatechange = function(){
        console.log(peerConnection.readyState);
    }

    peerConnection.onicecandidate = function(event){
        if (event.candidate){
            send({
                action: "candidate",
                data: event.candidate
            })
        }
    }

    peerConnection.ontrack = function(event){
        const reStream = event.streams[0]
        reStream.getVideoTracks()[0].onended = (event)=>{
            remoteVideo.style.visibility = 'hidden'
        } 
        remoteVideo.srcObject = reStream;
    }

    createOffer();
}

function createOffer(){
    navigator.getUserMedia(constraints, function (thisStream) { 
        localStream = thisStream;

        peerConnection.addStream(localStream);

        localStream.getVideoTracks()[0].enabled = document.querySelector('#video-checkbox').checked;
        localStream.getAudioTracks()[0].enabled = document.querySelector('#audio-checkbox').checked;

        peerConnection.createOffer(function(offer){
            peerConnection.setLocalDescription(offer)
            send({
                action: 'offer',
                data: offer,
            })
        }, function(error){
            console.log('createOffer error:', error)});

        localVideo.srcObject = localStream;
    
    }, function (error) {
        console.log('error: ', error)
    }); 
}

function handlerOffer(offer, channel_id){
    peerConnection.setRemoteDescription(offer)
        .then(() => {
            console.log('Set Remote Description', peer);
            return peerConnection.createAnswer()
        })
        .then(answer => {
            console.log('Answer create');
            peerConnection.setLocalDescription(answer).then(()=>{});

            send({
                action: "answer",
                data: answer
            })
        })
}

function handlerAnswer(answer){
    peerConnection.setRemoteDescription(new RTCSessionDescription(answer)).then(()=>console.log('SET REMOTE DESCRIPTION AFTER ANSWER'));

}

function handlerCandidate(candidate){
    peerConnection.addIceCandidate(new RTCIceCandidate(candidate)).then().catch(error=>console.log('error'));
}

document.querySelector('#audio-checkbox').addEventListener('change',(event)=>{
    if (clientSocket.readyState === 1){
        console.log('open');
        send({   
            full_name,
            action: 'change_audio',
            data: event.target.checked,
        })
        audio = localStream.getAudioTracks()[0].enabled = event.target.checked;
        if (event.target.checked){
            document.querySelector('#my_microphone_state').style.visibility = 'hidden';
        } else {
            document.querySelector('#my_microphone_state').style.visibility = 'visible';
        }
    } else {
        event.target.checked = !event.target.checked;
    }
})

document.querySelector('#video-checkbox').addEventListener('change', (event)=>{
    if (clientSocket.readyState === 1){
        send({
            full_name,
            action: 'change_camera',
            data: event.target.checked,
        })
        video = localStream.getVideoTracks()[0].enabled = event.target.checked;
        if (event.target.checked){
            localVideo.style.visibility = 'visible'
        } else {
            localVideo.style.visibility = 'hidden'
        }
    } else {
        event.target.checked = !event.target.checked;
    }
    console.log(peerConnection.readyState);
})

document.querySelector('#send-msg-btn').addEventListener('click', ()=>{
    let message = document.querySelector('#chat-input');
    console.log(clientSocket.readyState);
    if (clientSocket.readyState === 1){
        console.log(message.value)
        send({
            full_name,
            action: 'message',
            message: message.value,
        });
        let chat_log = document.querySelector('#chat-log');
        let message_item = document.createElement('li');
        message_item.textContent = `${full_name}: ${message.value}`;
        chat_log.append(message_item);
        message.value = '';
    }    
})

document.querySelector('#chat-input').addEventListener('keydown', (event)=>{
    if (event.keyCode === 13){
        document.querySelector('#send-msg-btn').click();
    }
})


function send_call_ending_status(status){
    const xhr = new XMLHttpRequest();
    let data = {};
    xhr.open('POST', `http://${window.location.host}/chat/end-call/${call_id}/`);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.setRequestHeader('x-requested-with', 'XMLHttpRequest');
    switch (status){
        case 'complaint':
            data['status'] = 'complaint';
            for (const input of document.querySelector('#complaint_form').elements){
                data[input.name] = input.value;
            }
            break;
        case 'review':
            data['status'] = 'review';
            for (const input of document.querySelector('#review_form').elements){
                data[input.name] = input.value;
            }
            break;
        case 'success':
            data['status'] = 'success';
            break;
    }
    data = JSON.stringify(data);
    console.log(data);
    xhr.onreadystatechange  = function(){
        if (xhr.readyState == XMLHttpRequest.DONE){
            response = JSON.parse(xhr.response);
            console.log(xhr.response);
            if (response.status === 'success'){
                send({
                    action: 'end_call',
                });
                end_call();
                document.querySelector('#call_end_info_content').innerHTML = response.message
            }
            if (response.status === 'success complaint'){
                send({
                    action: 'complaint',
                });
                send({
                    action:'complaint'
                })
                window.location.href = `http://${window.location.host}/moderation/complaint-info/initiator/`;
            }
        }
    }
    xhr.send(data);
}

document.querySelector('#end_call_btn').addEventListener('click', (event)=> {
    console.log(event.target);
    document.querySelector('#end_call_question').style.display = 'block';
});

let review_btn = document.querySelector('#review_btn');


if (review_btn){
    review_btn.addEventListener('click', (event)=> {
        send_call_ending_status('review')
    });
}

document.querySelector('#complaint_btn').addEventListener('click', (event)=> {
    console.log('bebra')
    send_call_ending_status('complaint')
});

for (let form of document.forms){
    for (let element in form.elements){
        element.onkeydown = function(event){
            event.preventDefault();
            return null;
        }
    }
}