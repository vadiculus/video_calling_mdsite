from django.shortcuts import render, get_object_or_404, redirect
from .models import PremiumChat, PremiumChatMessage, AdminChatMessage, AdminChat, OrderedCall
from django.http import Http404, JsonResponse
from accounts.models import User
from doctors.utils import require_premium_and_doctors, require_not_superusers
from django.db.models import Prefetch, Q
from moderation.utils import require_not_banned
from django.contrib.auth.views import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Prefetch
from doctors.forms import ReviewForm
from moderation.forms import ComplaintForm
from doctors.models import Review
from mdsite.utils import server_tz
from mdsite.settings import TIME_ZONE
from paynament.models import SiteBalance
from .tasks import send_user_mail
from django.contrib import messages
from moderation.models import StandardComplaint
import pytz
import datetime
import json

@require_not_superusers
@require_premium_and_doctors
@require_not_banned
def premium_chat(request, chat_id):
    chat = get_object_or_404(PremiumChat.objects.prefetch_related(
        Prefetch('premium_chat_messages', PremiumChatMessage.objects.select_related('author'))), pk=chat_id)
    chat_messages = chat.premium_chat_messages.all()
    interlocutor = chat.get_interlocutor(request.user) #Получаем собеседника

    chat.premium_chat_messages.all().update(read=True)

    if request.user.is_authenticated:
        if request.user.is_banned:
            title = 'Your account is banned'
            return render(request, 'errors/some_error.html', {'title': title})

        if interlocutor.is_banned:
            title = 'You cannot write to a banned account'
            return render(request, 'errors/some_error.html', {'title': title})

        if request.user not in chat.participants.all():
            title = 'You do not have access to this chat'
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
    chat.admin_chat_messages.filter(~Q(author=request.user) & Q(read=False)).update(read=True)

    chat.admin_chat_messages.all().update(read=True)

    if request.user.is_authenticated:
        if request.user not in chat.participants.all():
            title = 'You do not have access to this chat'
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
    ChatModel = AdminChat if user.is_staff else PremiumChat
    if not user.is_doctor: # Доктора не могут начинать чат
        if user.is_banned:
            title = 'Your account is banned'
            return render(request, 'errors/some_error.html', {'title': title})
        if interlocutor.is_banned:
            title = 'You cannot write to a banned account'
            return render(request, 'errors/some_error.html', {'title': title})

        try:
            chat = ChatModel.objects.filter(participants=user).get(participants=interlocutor)
        except ChatModel.DoesNotExist:
            chat = ChatModel.objects.create()
            chat.participants.set([user, interlocutor])

        if user.is_staff:
            return redirect(f'chat:admin_chat', chat.id)

        if user.client.is_premium:
            return redirect(f'chat:premium_chat', chat.id)

        title = "You have not premium"
        body = 'You can buy premium on your user page'
        return render(request, 'errors/some_error.html', {'title':title, 'body':body})
    title = "Doctor can't create a chat"
    return render(request, 'errors/some_error.html', {'title':title})

@require_not_banned
@require_not_superusers
@require_premium_and_doctors
def premium_chat_list_view(request):
    if not request.user.is_banned:
        chats = PremiumChat.objects.prefetch_related('participants').filter(participants=request.user)
        return render(request, 'chat/premium_chat_list.html', {'chats':chats})

@login_required
def admin_chat_list_view(request):
    chats = AdminChat.objects.prefetch_related('participants').filter(participants=request.user)
    return render(request, 'chat/admin_chat_list.html', {'chats':chats})

@require_not_banned
def ordered_call_view(request, pk):
    ordered_call = get_object_or_404(OrderedCall.objects.select_related('visiting_time'), pk=pk)
    if ordered_call.is_ended:
        raise Http404
    if ordered_call.is_active():
        interlocutor = ordered_call.get_interlocutor(request.user)
        return render(request, 'chat/ordered_call.html', {
            'call_id':pk,
            'call':ordered_call,
            'call_end_time': ordered_call.visiting_time.time_end - datetime.timedelta(minutes=1),
            'interlocutor': interlocutor,
            'review_form': ReviewForm(),
            'complaint_form': ComplaintForm(),
        })
    else:
        if request.user.is_doctor:
            title = "You've missed your call"
            body = 'A complaint has been filed against you'

            return render(request, 'errors/some_error.html', {'title': title, 'body':body})
        else:
            title = "You've missed your call"
            body = 'Your account has been debited for the call'
            return render(request, 'errors/some_error.html', {'title': title, 'body': body})

@require_not_banned
def ordered_call_list(request):
    ordered_calls = OrderedCall.objects.select_related('visiting_time')\
        .prefetch_related('participants').filter(Q(participants__id=request.user.id, is_ended=False))
    return render(request, 'chat/ordered_call_list.html', {'calls':ordered_calls})

@require_POST
def end_call(request, pk):
    try:
        call = OrderedCall.objects.prefetch_related(
            Prefetch('participants', User.objects.select_related('balance'))).get(pk=pk)
    except OrderedCall.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        client, doctor = call.get_client(), call.get_doctor()
        initiator = request.user
        data = json.loads(request.body)
        call_end_type = data.get('status')

        if initiator not in call.participants.all():
            return JsonResponse({'status': 'no permissions'})

        call.call_end = datetime.datetime.now(pytz.utc)
        call.is_ended = True
        call.have_complaint = True
        if not call.call_start:
            call.call_start = call.visiting_time.time
        call.save()
        site_balance = SiteBalance.objects.get(pk=1)
        percent = call.get_percent(doctor, site_balance)
        price = call.get_price(doctor)
        total_price = call.get_total_price(doctor, site_balance)

        def money_transfer():
            with transaction.atomic():
                client.balance.balance -= total_price
                site_balance.balance += call.get_percent(doctor, site_balance)
                doctor.balance.balance += price
                title = 'Call is successful'
                body = f'The call was successfully completed. Amount has been withdrawn from your account: {total_price}$'
                send_user_mail.delay(client.email, title, body)
                site_balance.save(), client.balance.save(), doctor.balance.save(),
                call.visiting_time.delete()
                return body

        if call_end_type == 'success':
            money_transfer()
            return JsonResponse({'status':'success'})

        if call_end_type == 'review':
            if not initiator.is_doctor:
                review_form = ReviewForm(data)
                if review_form.is_valid():
                    Review.objects.update_or_create(client=client.client, doctor=doctor.doctor,
                                                    defaults=review_form.cleaned_data)
                message = money_transfer()

                return JsonResponse({'status':'success', 'message': message})

        if call_end_type == 'complaint':
            complaint_form = ComplaintForm(data)
            if complaint_form.is_valid():
                with transaction.atomic():
                    complaint = complaint_form.save(commit=False)
                    complaint.initiator = initiator
                    complaint.accused = call.get_interlocutor(initiator)
                    complaint.ordered_call = call
                    complaint.price = price
                    client.balance.balance -= percent
                    site_balance.balance += percent
                    complaint.save()
                    call.visiting_time.delete()
                title = 'A complaint has been filed against you'
                body = 'A complaint has been filed against you. The administration will write to you shortly to resolve the problem.'
                send_user_mail.delay(client.email, title, body)
                return JsonResponse({'status':'success complaint'})
    else:
        return JsonResponse({'status': 'no xhr request'})

def show_price(request, pk):
    call = get_object_or_404(OrderedCall.objects.prefetch_related('participants'), pk=pk)
    total_price = call.get_total_price()
    return render(request, 'chat/show_price.html', {'total_price':total_price})

def cancel_ordered_call(request, pk):
    call = get_object_or_404(OrderedCall.objects.select_related('visiting_time')
                             .prefetch_related('participants'), pk=pk)
    if call.get_doctor() == request.user:
        if not call.is_active():
            message_body = f'Dr. { call.visiting_time.doctor } canceled the scheduled call'
            send_user_mail.delay(call.get_client().email, 'Conference cancellation', message_body)
            call.visiting_time.delete()
        else:
            messages.error(request, 'The call is already active, you cannot cancel the call.')
    return redirect('accounts:profile', request.user.username)

