from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
import json
import os
from .models import Video


def index(request):
    """Главная страница"""
    return render(request, 'index.html')


def gallery(request):
    """Страница галереи видео"""
    videos_list = Video.objects.all()
    per_page = 6
    
    paginator = Paginator(videos_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gallery.html', {
        'page_obj': page_obj,
        'per_page': per_page
    })


def video_detail(request, pk: int):
    """Детальная страница видео"""
    video = get_object_or_404(Video, pk=pk)
    
    # Если нет превью, пробуем создать
    if not video.thumbnail:
        video.generate_thumbnail_on_demand()
    
    return render(request, 'detail.html', {'video': video})


def conclusion(request):
    """Страница содержания"""
    videos = Video.objects.all()
    can_upload = request.user.is_authenticated and request.user.is_superuser
    return render(request, 'conclusion.html', {
        'videos': videos,
        'can_upload': can_upload
    })


def is_superuser(user):
    """Проверка на суперюзера"""
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_superuser)
def upload_video(request):
    """Страница загрузки видео (только для суперюзера)"""
    # Получаем видео без превью - используем isnull для правильной фильтрации
    videos_without_thumbnails = Video.objects.filter(thumbnail__isnull=True).order_by('-created_at')[:10]
    
    if request.method == 'POST':
        try:
            video_file = request.FILES.get('video')
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            duration = request.POST.get('duration', '')
            
            if not video_file:
                messages.error(request, 'Пожалуйста, выберите видео файл')
                return render(request, 'upload.html', {
                    'videos_without_thumbnails': videos_without_thumbnails
                })
            
            # Валидация размера
            if video_file.size > 500 * 1024 * 1024:
                messages.error(request, 'Размер файла не должен превышать 500MB')
                return render(request, 'upload.html', {
                    'videos_without_thumbnails': videos_without_thumbnails
                })
            
            # Валидация расширения
            ext = video_file.name.split('.')[-1].lower()
            allowed_exts = ['mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v', '3gp']
            if ext not in allowed_exts:
                messages.error(request, f'Недопустимый формат. Разрешены: {", ".join(allowed_exts)}')
                return render(request, 'upload.html', {
                    'videos_without_thumbnails': videos_without_thumbnails
                })
            
            # Создаём видео (конвертация и превью создадутся автоматически в модели)
            video = Video.objects.create(
                title=title or video_file.name,
                description=description,
                video=video_file,
                duration=duration
            )
            
            messages.success(request, f'Видео "{video.title}" успешно загружено!')
            return redirect('upload_videos')
            
        except Exception as e:
            messages.error(request, f'Ошибка при загрузке: {str(e)}')
            return render(request, 'upload.html', {
                'videos_without_thumbnails': videos_without_thumbnails
            })
    
    return render(request, 'upload.html', {
        'videos_without_thumbnails': videos_without_thumbnails
    })


@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def delete_video(request, pk):
    """Удаление видео (только для суперюзера)"""
    try:
        video = get_object_or_404(Video, pk=pk)
        video_title = video.title or f"Видео #{video.pk}"
        
        # Удаляем файлы
        if video.video:
            video_path = video.video.path
            if os.path.exists(video_path):
                os.remove(video_path)
        if video.thumbnail:
            thumb_path = video.thumbnail.path
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        
        video.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Видео "{video_title}" успешно удалено!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при удалении: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def edit_video(request, pk):
    """Редактирование видео (только для суперюзера)"""
    try:
        video = get_object_or_404(Video, pk=pk)
        
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value', '')
        
        if field == 'title':
            video.title = value
            video.save()
            return JsonResponse({
                'success': True,
                'message': 'Название успешно обновлено!'
            })
        elif field == 'description':
            video.description = value
            video.save()
            return JsonResponse({
                'success': True,
                'message': 'Описание успешно обновлено!'
            })
        elif field == 'duration':
            video.duration = value
            video.save()
            return JsonResponse({
                'success': True,
                'message': 'Длительность успешно обновлена!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Неподдерживаемое поле'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при редактировании: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def generate_thumbnail(request, pk):
    """Создание превью для видео по запросу"""
    try:
        video = get_object_or_404(Video, pk=pk)
        video.generate_thumbnail_on_demand()
        
        # Проверяем создалось ли превью
        thumbnail_created = False
        if video.thumbnail:
            try:
                thumbnail_created = os.path.exists(video.thumbnail.path)
            except:
                pass
        
        if thumbnail_created:
            return JsonResponse({
                'success': True,
                'message': 'Превью успешно создано!',
                'thumbnail_url': video.thumbnail.url
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Не удалось создать превью. Проверьте, что FFmpeg установлен и видео не повреждено.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка: {str(e)}'
        })


# =============================================================================
# СИСТЕМА АВТОРИЗАЦИИ
# =============================================================================

def user_login(request):
    """Страница входа"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему!')
                return redirect('conclusion')
            else:
                messages.error(request, 'У вас нет прав администратора')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'login.html')


@login_required
def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')