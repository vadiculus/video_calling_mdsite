from django.http import Http404
from django.shortcuts import render

def require_doctors(view):
    def get_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_doctor:
                return view(request, *args, **kwargs)
            else:
                raise Http404
        else:
            title = 'Вы не аторизовыны'
            return render(request, 'errors/some_error.html', {'title': title})

    return get_view

def require_confirmed_doctors(view):
    def get_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_doctor:
                if user.doctor.is_confirmed:
                    return view(request, *args, **kwargs)
                else:
                    title = 'Ваша заявка не подтвержена модерацией'
                    return render(request, 'errors/some_error.html', {'title': title})
            else:
                raise Http404
        else:
            title = 'Вы не аторизовыны'
            return render(request, 'errors/some_error.html', {'title': title})

def require_clients(view):
    def get_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_doctor:
                return view(request, *args, **kwargs)
            else:
                raise Http404
        else:
            title = 'Вы не аторизовыны'
            return render(request, 'errors/some_error.html', {'title': title})

    return get_view

def require_premium(view):
    def get_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_doctor:
                if request.user.client.is_premium:
                    return view(request, *args, **kwargs)
                title = 'Вы не имеете премиум аккаунта'
                body = 'Вы можете купить премиум аккаунт на своей странице профиля'
                return render(request, 'errors/some_error.html', {'title': title, 'body': body})
            else:
                raise Http404
        else:
            title = 'Вы не аторизовыны'
            return render(request, 'errors/some_error.html', {'title': title})

    return get_view

def require_premium_and_doctors(view):
    def get_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_doctor:
                if user.doctor.is_confirmed:
                    return view(request, *args, **kwargs)
                else:
                    title = 'Ваша заявка не подтвержена модерацией'
                    return render(request, 'errors/some_error.html', {'title': title})
            else:
                if user.client.is_premium:
                    return view(request, *args, **kwargs)
                title = 'Вы не имеете премиум аккаунта'
                body = 'Вы можете купить премиум аккаунт на своей странице профиля'
                return render(request, 'errors/some_error.html', {'title': title, 'body': body})
        else:
            title = 'Вы не аторизовыны'
            return render(request, 'errors/some_error.html', {'title': title})

    return get_view

def require_not_superusers(view):
    def get_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return view(request, *args, **kwargs)
        else:
            title = 'Для администраторов запрещена функция чата'
            return render(request, 'errors/some_error.html', {'title': title})

    return get_view
