let photos_input = document.querySelector('#id_certification_photos');
photos_input.addEventListener('change', (event)=>{
    console.log('check')
    if (photos_input.files.length > 5){
        for (let i = 0; i < photos_input.files.length; i++) {
            const file = photos_input.files[i];
            if (file.size > maxFileSize) {
              invalidFiles.push(file.name);
            }
          }
        alert('Разрешено максимум 5 файлов');
    }
})