from django.shortcuts import render, get_object_or_404, redirect
from .models import PremiumChat, PremiumChatMessage, AdminChatMessage, AdminChat, OrderedCall
from django.http import Http404
from accounts.models import User
from doctors.utils import require_premium_and_doctors, require_not_superusers
from django.db.models import Prefetch
from moderation.utils import require_not_banned
from django.contrib.auth.views import login_required
import pytz
import datetime

@require_not_superusers
@require_premium_and_doctors
@require_not_banned
def premium_chat(request, chat_id):
    chat = get_object_or_404(PremiumChat.objects.prefetch_related(
        Prefetch('premium_chat_messages', PremiumChatMessage.objects.select_related('author'))), pk=chat_id)
    chat_messages = chat.premium_chat_messages.all()
    interlocutor = chat.get_interlocutor(request.user) #Получаем собеседника

    if request.user.is_authenticated:
        if request.user.is_banned:
            title = 'Ваш аккаунт заблокирован'
            return render(request, 'errors/some_error.html', {'title': title})

        if interlocutor.is_banned:
            title = 'Вы не можете написать заблокированному аккаунту'
            return render(request, 'errors/some_error.html', {'title': title})

        if request.user not in chat.participants.all():
            title = 'У вас нету доступа к этом чату'
            return render(request, 'errors/some_error.html', {'title': title})
        return render(request, 'chat/premium_chat.html', {
            'chat_id': chat_id,
            'chat_messages':chat_messages,
            'chat':chat,
            'interlocutor': chat.get_interlocutor(request.user)})
    else:
        raise Http404

@login_required
def admin_chat(request, chat_id):
    chat = get_object_or_404(AdminChat.objects.prefetch_related(
        Prefetch('admin_chat_messages', AdminChatMessage.objects.select_related('author'))), pk=chat_id)
    chat_messages = chat.admin_chat_messages.all()
    if request.user.is_authenticated:
        if request.user not in chat.participants.all():
            title = 'У вас нету доступа к этом чату'
            return render(request, 'errors/some_error.html', {'title': title})
        return render(request, 'chat/admin_chat.html', {
            'chat_id': chat_id,
            'chat_messages':chat_messages,
            'chat':chat,
            'interlocutor': chat.get_interlocutor(request.user)})
    else:
        raise Http404

@require_not_banned
def create_chat(request, username):
    user = request.user
    interlocutor = get_object_or_404(User, username=username)
    ChatModel = AdminChat if user.is_superuser else PremiumChat
    if not user.is_doctor: # Доктора не могут начинать чат
        if user.is_banned:
            title = 'Ваш аккаунт заблокирован'
            return render(request, 'errors/some_error.html', {'title': title})
        if interlocutor.is_banned:
            title = 'Вы не можете написать заблокированному аккаунту'
            return render(request, 'errors/some_error.html', {'title': title})

        try:
            chat = ChatModel.objects.filter(participants=user).get(participants=interlocutor)
        except ChatModel.DoesNotExist:
            chat = ChatModel.objects.create()
            chat.participants.set([user, interlocutor])

        if user.is_superuser:
            return redirect(f'chat:admin_chat', chat.id)

        if user.client.is_premium:
            return redirect(f'chat:premium_chat', chat.id)

        title = 'Вы не имеете премиум аккаунта'
        body = 'Вы можете купить премиум аккаунт на своей странице профиля'
        return render(request, 'errors/some_error.html', {'title':title, 'body':body})
    title = 'Доктора не могут создавать чаты'
    return render(request, 'errors/some_error.html', {'title':title})

@require_not_superusers
@require_premium_and_doctors
def premium_chat_list_view(request):
    chats = PremiumChat.objects.prefetch_related('participants').filter(participants=request.user)
    return render(request, 'chat/premium_chat_list.html', {'chats':chats})

@login_required
def admin_chat_list_view(request):
    chats = AdminChat.objects.prefetch_related('participants').filter(participants__id__in=[request.user.id])
    return render(request, 'chat/admin_chat_list.html', {'chats':chats})

@require_not_banned
def ordered_call_view(request, pk):
    ordered_call = get_object_or_404(OrderedCall.objects.select_related('visiting_time'), pk=pk)
    if ordered_call.is_active():
        return render(request, 'chat/ordered_call.html', {'call_id':pk, 'call':ordered_call})
    else:
        if request.user.is_doctor:
            title = 'Вы пропусти свое время'
            body = 'На вас была поданна жалоба'
            return render(request, 'errors/some_error.html', {'title': title, 'body':body})
        else:
            title = 'Вы пропусти свое время'
            body = 'С вашего счета была списана сумма за звонок'
            return render(request, 'errors/some_error.html', {'title': title, 'body': body})

@require_not_banned
def ordered_call_list(request):
    ordered_calls = OrderedCall.objects.select_related('visiting_time')\
        .prefetch_related('participants').filter(participants__id=request.user.id)
    return render(request, 'chat/ordered_call_list.html', {'calls':ordered_calls})

