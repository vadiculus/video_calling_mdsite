from django.contrib import admin
from accounts.models import User, Client
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

class ClientAdmin(admin.ModelAdmin):
    search_fields = ['user__full_name', 'user__username']
    list_display = ['full_name','username']
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

class UserAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'username']
    list_display = ['full_name', 'username']
    list_display_links = ['full_name']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = super().get_object(request, object_id)
        return redirect('accounts:profile', obj.username)

admin.site.register(User, UserAdmin)
# admin.site.register(Client, ClientAdmin)