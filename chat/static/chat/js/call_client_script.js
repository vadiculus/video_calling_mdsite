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

clientSocket.addEventListener('message', (event)=>{
    message = JSON.parse(event['data']);

    console.log(message);

    if (message.peer === peer){
        return;
    }

    console.log(message);
    
    switch (message.action){
        case 'offer':
            handlerOffer(message.data)
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
        
            peerConnection.setLocalDescription(offer);
    
            send({
                action: 'offer',
                data: offer
            });
    
        }, function(error){


        console.log('createOffer error:', error)});

        localVideo.srcObject = localStream;
    
    }, function (err) {
        console.log('error: ', error)
    }); 
}

function handlerOffer(offer){    
    createDataChannel();
    peerConnection.setRemoteDescription(offer)
        .then(() => {
            console.log('Set Remote Description', peer);
            return peerConnection.createAnswer()
        })
        .then(answer => {
            console.log('Answer create');
            peerConnection.setLocalDescription(answer)

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
// при подклчении не меняется

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

function createDataChannel(){
    console.log('createDataChannel')
    dataChannel = peerConnection.createDataChannel("dataChannel", {
        reliable: true
    })

    dataChannel.onopen = function(){
        console.log('dataChannel opened');
        remoteVideo.style.visibility = 'visible';
        document.querySelector('#connection_state').style.display = 'none';
    }

    dataChannel.onclosing = function(){
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