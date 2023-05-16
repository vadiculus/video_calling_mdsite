for (let message of document.querySelectorAll('.message')){
    let date = new Date(message.dataset.time);
    let hour = date.getHours() < 10 ? '0' + date.getHours() : date.getHours();
    let minute = date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes();
    let time_element = document.createElement('span');
    time_element.innerHTML += `${hour}:${minute}`;
    message.append(document.createElement('br'));
    message.append(time_element);
}