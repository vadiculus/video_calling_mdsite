from django.shortcuts import render, redirect

from moderation.utils import require_not_banned
from .forms import BalanceReplenishmentForm, SiteBalanceUpdateForm
from django.contrib.auth.views import login_required
from doctors.utils import require_clients
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import SiteBalance

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


class SiteBalanceUpdateView(UpdateView):
    form_class = SiteBalanceUpdateForm
    template_name = 'paynament/update_site_balance.html'
    success_url = reverse_lazy('admin:index')
    queryset = SiteBalance

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['site_balance'] = self.get_object().balance
        return context

    def get_object(self, queryset=None):
        site_balance, _ = SiteBalance.objects.get_or_create(pk=1, defaults={'percent':3})
        return site_balance

