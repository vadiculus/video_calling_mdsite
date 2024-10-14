
# video calling medical site
video_calling_mdsite is a site made for online health consultations.
Doctors set times when they can take calls, and clients reserve these times.
Calls are implemented using the WebRTC protocol.
The site also has a system of moderation, reviews, and chats based on websockets.

This site was my first working experience and the task was quite big.
I was the only one doing all the work, and there was no time left for Frontend. Don't judge harshly)

Due to the short deadlines, the project remains unfinished and it also has bugs and vulnerabilities, but the basic functions work fine.

### How to start a project
You need __python-3.10__, __celery__, __redis__.

cmd
```
    pip install -r requirements.txt
    pip install Pillow
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    
    "Turn on Redis"

    celery -A mdsite worker
    python manage.py runserver localhost:8000

    "Works only on loopback-interface, because browser doesn't work with media divices without HTTPS protol."
```
