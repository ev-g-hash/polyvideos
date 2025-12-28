from django.shortcuts import render
from django.contrib import messages


def index(request):
    """
    Главная страница - Poly Videos
    """
    context = {
        'page_title': 'Poly Videos',
    }
    return render(request, 'index.html', context)


def gallery(request):
    """
    Страница галереи видео
    """
    # В будущем здесь будет загрузка из базы данных
    context = {
        'page_title': 'Галерея Видео',
    }
    return render(request, 'gallery.html', context)


def admin(request):
    """
    Страница админ-панели (авторизация)
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Демо-проверка (в будущем - Django auth)
        if username == 'admin' and password == 'admin123':
            messages.success(request, 'Добро пожаловать в админ панель!')
            # В реальном приложении здесь был бы переход
        else:
            messages.error(request, 'Неверный логин или пароль!')
    
    context = {
        'page_title': 'Админ Панель',
    }
    return render(request, 'admin.html', context)