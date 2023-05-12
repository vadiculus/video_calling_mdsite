from django.contrib import admin
from .models import Doctor, Qualification, Review
from django.shortcuts import redirect

class DoctorAdmin(admin.ModelAdmin):
    search_fields = ['user__full_name', 'user__username']
    list_display = ['full_name', 'username']
    list_display_links = ['username']

    def username(self, obj):
        return obj.user.username

    def full_name(self, obj):
        return obj.user.full_name

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = super().get_object(request, object_id)
        return redirect('accounts:profile', obj.user.username)

    def get_queryset(self, request):
        queryset = self.model.objects.select_related('user')
        return queryset

    # def has_change_permission(self, request, obj=None):
    #     return False

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Qualification)
admin.site.register(Review)
