from django.db import models
from django.conf import settings
import os
import uuid
import cv2
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile


def video_upload_path(instance, filename):
    """Генерирует путь для сохранения видео файла"""
    ext = filename.split('.')[-1].lower()
    
    if instance.pk:
        filename_base = str(instance.pk)
    else:
        filename_base = f"temp_{uuid.uuid4().hex[:8]}"
    
    return os.path.join('videos/', f"{filename_base}.{ext}")


def thumbnail_upload_path(instance, filename):
    """Путь для сохранения превью"""
    try:
        video_id = instance.video.id
    except (AttributeError, ValueError):
        video_id = instance.pk or uuid.uuid4().hex[:8]
    return os.path.join('thumbnails/', f"{video_id}.jpg")


def validate_video_size(video):
    """Валидация размера видео файла"""
    max_size = 500 * 1024 * 1024  # 500MB
    if video.size > max_size:
        raise ValidationError(f'Размер файла не должен превышать 500MB')


def validate_video_extension(video):
    """Валидация расширения видео файла"""
    ext = video.name.split('.')[-1].lower()
    allowed_exts = ['mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v', '3gp']
    if ext not in allowed_exts:
        raise ValidationError(f'Недопустимый формат файла. Разрешены: {", ".join(allowed_exts)}')


class Video(models.Model):
    """Модель видео"""
    title = models.CharField('Название', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    video = models.FileField(
        'Видео файл',
        upload_to=video_upload_path,
        validators=[validate_video_size, validate_video_extension]
    )
    thumbnail = models.ImageField(
        'Превью', 
        upload_to=thumbnail_upload_path, 
        blank=True, 
        null=True,
        help_text='Будет создано автоматически из видео'
    )
    duration = models.CharField('Длительность', max_length=20, blank=True, help_text='Например: 3:45')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    # Поле для хранения оригинального формата
    original_format = models.CharField('Оригинальный формат', max_length=10, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'

    def __str__(self):
        return self.title or f'Видео #{self.pk}'

    def get_file_size_mb(self):
        """Возвращает размер файла в МБ"""
        try:
            if self.video:
                size_bytes = self.video.size
                return round(size_bytes / (1024 * 1024), 2)
        except:
            pass
        return None
    
    def save(self, *args, **kwargs):
        """Переопределяем сохранение для создания превью"""
        is_new = self.pk is None
        
        # Сохраняем оригинальный формат до сохранения
        if self.video and hasattr(self.video, 'name'):
            ext = self.video.name.split('.')[-1].lower() if '.' in self.video.name else ''
            self.original_format = ext
        
        super().save(*args, **kwargs)
        
        # Создаём превью из видео (после первого сохранения)
        if is_new and self.video:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        """Создаёт превью из первого кадра видео (без FFmpeg, используя OpenCV)"""
        if not self.video:
            return
        
        try:
            video_path = self.video.path
            
            # Проверяем существует ли файл
            if not os.path.exists(video_path):
                print(f"Видео файл не найден: {video_path}")
                return
            
            # Путь для сохранения превью
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_path = os.path.join(thumbnail_dir, f'{self.pk}.jpg')
            
            # Используем OpenCV - FFmpeg НЕ НУЖЕН!
            cap = cv2.VideoCapture(video_path)
            success, frame = cap.read()
            cap.release()
            
            if success:
                # Конвертируем BGR (OpenCV) в RGB (PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Создаём изображение из массива numpy
                img = Image.fromarray(frame_rgb)
                
                # Изменяем размер (опционально)
                img = img.resize((480, 270), Image.Resampling.LANCZOS)
                
                # Сохраняем
                img.save(thumbnail_path, 'JPEG', quality=85)
                img.close()
                
                # Обновляем поле thumbnail в базе
                with open(thumbnail_path, 'rb') as f:
                    self.thumbnail.save(f'{self.pk}.jpg', ContentFile(f.read()), save=True)
                
                print(f"✅ Превью для видео #{self.pk} создано (OpenCV)")
            else:
                print(f"❌ Не удалось извлечь кадр из видео #{self.pk}")
                
        except Exception as e:
            print(f"❌ Ошибка создания превью для видео #{self.pk}: {e}")
    
    def generate_thumbnail_on_demand(self):
        """Создаёт превью по запросу (если отсутствует)"""
        thumbnail_exists = False
        if self.thumbnail:
            try:
                thumbnail_exists = os.path.exists(self.thumbnail.path)
            except:
                pass
        
        if not thumbnail_exists:
            self.create_thumbnail()