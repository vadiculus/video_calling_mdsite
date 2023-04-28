from django.contrib import admin
from .models import Doctor, Qualification

class DoctorAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = self.model.objects.select_related('user')
        return queryset

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Doctor)
admin.site.register(Qualification)
