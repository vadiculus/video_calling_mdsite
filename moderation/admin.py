from django.contrib import admin
from .models import CertificationConfirmation, Complaint, StandardComplaint
from django.utils.safestring import mark_safe
from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.urls import reverse_lazy


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

    photos.short_description = 'Photo certificates'


class ComplaintAdmin(admin.ModelAdmin):
    fields = ['initiator', 'accused', 'cause']
    change_form_template = 'moderation/admin/complaint_change_form.html'
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

class StandardComplaintAdmin(admin.ModelAdmin):
    fields = ['initiator', 'accused', 'cause']
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

admin.site.register(CertificationConfirmation, CertificationConfirmationAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(StandardComplaint, StandardComplaintAdmin)

