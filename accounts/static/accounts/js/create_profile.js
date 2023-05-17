let photos_input = document.querySelector('#id_certification_photos');
photos_input.addEventListener('change', (event)=>{
    console.log('check')
    if (photos_input.files.length > 5){
        alert('Разрешено максимум 5 файлов');
        photos_input.value = '';
    }
})