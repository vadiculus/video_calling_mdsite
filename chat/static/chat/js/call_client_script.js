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

console.log(remoteVideo);

const config = {
    iceServers: [
        {
            urls: "stun:stun.l.google.com:19302"
        },
    ]
}

// initialize();

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
            break;
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

    dataChannel = peerConnection.createDataChannel("dataChannel", {
        reliable: true
    })

    dataChannel.onopen = function(){
        console.log('dataChannel opened');
    }

    dataChannel.onclosing = function(){
        console.log('dataChannel closed');
        remoteVideo.srcObject = null;
    }

    dataChannel.onmessage = (event)=>{
        data = JSON.parse(event.data)
        let chat_log = document.querySelector('#chat-log');
        let message_item = document.createElement('li');
        message_item.textContent = `${data.full_name}: ${data.message}`;
        chat_log.append(message_item);
    }

    peerConnection.ontrack = function(event){
        const reStream = event.streams[0]
        remoteVideo.srcObject = reStream;
    }

    navigator.getUserMedia(constraints, function (thisStream) { 
        localStream = thisStream;

        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });

        peerConnection.ondatachannel = function(event){
            dataChannel = event.channel;
        }
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
    
    }, function (err) {console.log(error)}); 


}

function handlerOffer(offer){    
    peerConnection.setRemoteDescription(new RTCSessionDescription(offer));

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
    audio = localStream.getAudioTracks()[0].enabled = event.target.checked;
})


document.querySelector('#video-checkbox').addEventListener('change',(event)=>{
    video = localStream.getVideoTracks()[0].enabled = event.target.checked;
})

document.querySelector('#send-msg-button').addEventListener('click', ()=>{
    let message = document.querySelector('#chat-input');
    if (dataChannel.readyState === 'open'){
        console.log(message.value)
        dataChannel.send(JSON.stringify({full_name,message: message.value}));
        message.value = '';
    }    
})
