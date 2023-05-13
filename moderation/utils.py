from django.http import Http404
from django.shortcuts import render

def require_not_banned(view):
    def get_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_banned:
                return view(request, *args, **kwargs)
            else:
                title = 'Ваш аккаунт заблокирован'
                body = 'Вы не можете пользоваться этим функционалом так как ваш аккаунт заблокирован'
                return render(request, 'errors/some_error.html', {'title': title, 'body':body})
        else:
            raise Http404

    return get_view

def require_staff(view):
    def get_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return view(request, *args, **kwargs)
            else:
                raise Http404
        else:
            raise Http404

    return get_view
