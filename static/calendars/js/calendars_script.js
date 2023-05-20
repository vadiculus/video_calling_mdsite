let calendar_data = JSON.parse(document.querySelector('#calendar_script').textContent);
let calendar_container = document.querySelector('#calendar_container');

console.log(calendar_data);

for (const day of Object.keys(calendar_data)){
    let day_element = document.createElement('div');
    day_element.classList.add('calendar_day_item')
    let date = new Date(day);
    day_element.innerHTML = `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()}`;
    for (const time of calendar_data[day]){
        console.log(time);
        let time_element;
        if (!time.is_booked){
            time_element = document.createElement('a');
            time_element.href = `http://${window.location.host}/calendars/book-a-call/${time.id}/`;
        } else {
            time_element = document.createElement('span');
            time_element.style.color = 'red';
        }
        let time_date = new Date(time.time);
        let time_end = new Date(time.time_end);
        let hour = time_date.getHours() < 10 ? '0' + time_date.getHours() : time_date.getHours();
        let minute = time_date.getMinutes() < 10 ? '0' + time_date.getMinutes() : time_date.getMinutes();
        let hour_end = time_end.getHours() < 10 ? '0' + time_end.getHours() : time_end.getHours();
        let minute_end = time_end.getMinutes() < 10 ? '0' + time_end.getMinutes() : time_end.getMinutes();
        time_element.innerHTML = `${hour}:${minute}-${hour_end}:${minute_end}`;

        day_element.append(document.createElement('br'));
        day_element.append(time_element);
    }
    calendar_container.append(day_element);

}