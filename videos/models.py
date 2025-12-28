from django.db import models
import os
import uuid
from django.core.exceptions import ValidationError


def video_upload_path(instance, filename):
    """Генерирует путь для сохранения видео файла"""
    ext = filename.split('.')[-1].lower()
    
    # Разрешённые расширения
    allowed_exts = ['mp4', 'webm', 'mov', 'avi', 'mkv']
    if ext not in allowed_exts:
        ext = 'mp4'
    
    if instance.pk:
        filename_base = str(instance.pk)
    else:
        filename_base = f"temp_{uuid.uuid4().hex[:8]}"
    
    return os.path.join('videos/', f"{filename_base}.{ext}")


def validate_video_size(video):
    """Валидация размера видео файла"""
    max_size = 500 * 1024 * 1024  # 500MB
    if video.size > max_size:
        raise ValidationError(f'Размер файла не должен превышать 500MB')


def validate_video_extension(video):
    """Валидация расширения видео файла"""
    ext = video.name.split('.')[-1].lower()
    allowed_exts = ['mp4', 'webm', 'mov', 'avi', 'mkv']
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
    thumbnail = models.ImageField('Превью', upload_to='thumbnails/', blank=True, null=True)
    duration = models.CharField('Длительность', max_length=20, blank=True, help_text='Например: 3:45')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

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