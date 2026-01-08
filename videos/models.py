from django.db import models
import os
import uuid
import subprocess
import shutil
from django.core.exceptions import ValidationError
from django.conf import settings


def video_upload_path(instance, filename):
    """Генерирует путь для сохранения видео файла"""
    ext = filename.split('.')[-1].lower()
    
    # Все видео сохраняем как MP4 для совместимости
    if instance.pk:
        filename_base = str(instance.pk)
    else:
        filename_base = f"temp_{uuid.uuid4().hex[:8]}"
    
    return os.path.join('videos/', f"{filename_base}.mp4")


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
    thumbnail = models.ImageField('Превью', upload_to='thumbnails/', blank=True, null=True)
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
        """Переопределяем сохранение для конвертации в MP4"""
        is_new = self.pk is None
        
        # Сохраняем оригинальный формат до сохранения
        if self.video and hasattr(self.video, 'name'):
            ext = self.video.name.split('.')[-1].lower() if '.' in self.video.name else ''
            self.original_format = ext
        
        super().save(*args, **kwargs)
        
        # Конвертируем в MP4 если загружен не mp4
        if is_new and self.video:
            ext = self.original_format.lower()
            if ext and ext != 'mp4':
                self.convert_to_mp4()
    
    def convert_to_mp4(self):
        """Конвертирует видео в формат MP4 (H.264) для совместимости"""
        if not self.video:
            return
            
        ext = self.original_format.lower()
        if ext == 'mp4':
            return
            
        try:
            input_path = self.video.path
            output_path = input_path.replace(f'.{ext}', '.mp4')
            
            # Проверяем наличие ffmpeg
            if not shutil.which('ffmpeg'):
                print("FFmpeg не найден, пропускаем конвертацию")
                return
            
            # Команда для конвертации в MP4 с кодеком H.264
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                output_path
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Удаляем оригинальный файл
            if os.path.exists(input_path):
                os.remove(input_path)
            
            # Обновляем путь к файлу
            new_filename = os.path.basename(output_path)
            self.video.name = os.path.join('videos/', new_filename)
            
            # Обновляем запись в базе
            super().save(update_fields=['video'])
            
            print(f"Видео #{self.pk} конвертировано в MP4")
            
        except Exception as e:
            print(f"Ошибка конвертации видео #{self.pk}: {e}")