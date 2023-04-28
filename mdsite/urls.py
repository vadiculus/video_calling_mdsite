from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('doctoradminonline/', admin.site.urls),
    path('', include('doctors.urls', namespace='doctors')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('moderation/', include('moderation.urls', namespace='moderation')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
