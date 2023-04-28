from django.contrib import admin
from .models import CertificationConfirmation
from django.utils.safestring import mark_safe

class CertificationConfirmationAdmin(admin.ModelAdmin):
    readonly_fields = ['photos']
    change_form_template = 'moderation/admin/change_form.html'

    def photos(self, obj):
        photos_html = ''
        for photo in obj.certificationphoto_set.all():
            photos_html += f'<a href="{photo.photo.url}" data-fancybox="gallery" data-caption="Single image"">' \
                           f'<img src="{photo.photo.url}" width="200px"></a><br>'
        return mark_safe(photos_html)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def doctor_model(self, obj):
    #     doctor = obj.doctor
    #     qualifications = ''
    #     for qualification in doctor.qualification.all():
    #         qualifications += f'{qualification.name}, '
    #     return mark_safe(f'Имя: <b>{doctor.user.full_name}</b><br>Квалификации: {qualifications}')

    photos.short_description = 'Фото сертифифкатов'



admin.site.register(CertificationConfirmation, CertificationConfirmationAdmin)

