from django.shortcuts import render, redirect

from moderation.utils import require_not_banned
from .forms import BalanceReplenishmentForm
from django.contrib.auth.views import login_required
from doctors.utils import require_clients

@login_required
@require_clients
@require_not_banned
def top_up_balance(request):
    user = request.user
    form = BalanceReplenishmentForm
    if request.method == 'POST':
        form = BalanceReplenishmentForm(request.POST)
        if form.is_valid():
            user.balance.balance += form.cleaned_data['amount']
            user.balance.save()
            return redirect('accounts:profile', username=user.username)
    return render(request, 'paynament/top_up_balance.html', {'form':form})

