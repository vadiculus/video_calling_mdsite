for (let call of document.querySelectorAll('.call_time')){
    let date = new Date(call.dataset.date);
    let day = date.getDate() < 10 ? '0' + date.getDate() : date.getDate();
    let month = date.getMonth() < 10 ? '0' + date.getMonth() : date.getMonth();
    let year = date.getFullYear() < 10 ? '0' + date.getFullYear() : date.getFullYear();
    let hour = date.getHours() < 10 ? '0' + date.getHours() : date.getHours();
    let minute = date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes();
    call.innerHTML = `${day}.${month}.${year} ${hour}:${minute}`;
}