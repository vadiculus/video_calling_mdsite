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
const endTimeStr = JSON.parse(document.querySelector('#call_end_time').textContent);
const endTime = new Date(endTimeStr);
const csrftoken = getCookie('csrftoken');
let timer;

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

function end_call(){
    document.querySelector('#call_interface_container').style.display = 'none';
    document.querySelector('#end_call_question').style.display = 'none';
    document.querySelector('#call_end_info').style.display = 'block';
    send_call_ending_status('success');
    peerConnection.close();
    dataChannel.close();
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

clientSocket.addEventListener('message', (event)=>{
    message = JSON.parse(event['data']);

    if (message.peer === peer || (!peer && message.action != 'get_peer_name')){
        return;
    }

    // console.log(message);
    
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
            console.log('<ESSAGE',message.data.channel_id);
            initializeChannelId = message.data.channel_id;
            initialize()
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
            break;
        case 'complaint':
            // window.location.href = `http://${window.location.host}/moderation/complaint_info/accused/`;
            break;
        case 'create_dataChannel':
            console.log('CREATE_DATACHANNEL Remote')
            console.log(message.data);
            createDataChannel(message.data.label, message.data)
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

    peerConnection.ondatachannel = function(event){
        dataChannel = event.channel;
        console.log('CREATE_DATACHANNEL MY')
    }

    createDataChannel(initializeChannelId);

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
    
    }, function (error) {
        console.log('error: ', error)
    }); 
}

function handlerOffer(offer, channel_id){
    dataChannel.close();
    // createDataChannel(channel_id)
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
        });
}

function handlerAnswer(answer){
    peerConnection.setRemoteDescription(new RTCSessionDescription(answer)).then(()=>console.log(peerConnection.remoteDescription));
}

function handlerCandidate(candidate){
    peerConnection.addIceCandidate(new RTCIceCandidate(candidate)).then().catch(error=>console.log('error'));
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

document.querySelector('#send-msg-btn').addEventListener('click', ()=>{
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
        document.querySelector('#send-msg-btn').click();
    }
})

function createDataChannel(channel_id, data=null){
    if (!data){
        console.log('NO DATA');
        dataChannel = peerConnection.createDataChannel(channel_id, {
            reliable: true});

        send({
            action:'create_dataChannel',
            data: {
                id: dataChannel.id,
                streamId: dataChannel.streamId,
                name: dataChannel.label
            }
        })
    } else {
        console.log('DATA');
        dataChannel = peerConnection.createDataChannel(channel_id, {
            reliable: true}, id=data.id, streamId=data.streamId);
    }

    dataChannel.onopen = function(){
        console.log('dataChannel opened');
        remoteVideo.style.visibility = 'visible';
        document.querySelector('#connection_state').style.display = 'none';
    }

    dataChannel.onclose = function(){
        console.log('dataChannel closed');
        // remoteVideo.srcObject = null;
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

            case 'end_call':
                break;

            case 'message':
                let chat_log = document.querySelector('#chat-log');
                let message_item = document.createElement('li');
                message_item.textContent = `${data.full_name}: ${data.message}`;
                chat_log.append(message_item);
                break;
                
            case 'complaint':
                window.location.href = `http://${window.location.host}/moderation/complaint-info/accused/`;
                break;
            case 'call_end':
                end_call();
                break;
        }
    }
}

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
                dataChannel.send(JSON.stringify({
                    action: 'call_end',
                }));
                end_call();
                document.querySelector('#call_end_info_content').innerHTML = response.message
            }
            if (response.status === 'success complaint'){
                dataChannel.send(JSON.stringify({
                    action: 'complaint',
                }));
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