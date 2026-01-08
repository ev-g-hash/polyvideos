from django.db import models
from django.conf import settings
import os
import uuid
import subprocess
import shutil
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile


def video_upload_path(instance, filename):
    """Генерирует путь для сохранения видео файла"""
    ext = filename.split('.')[-1].lower()
    
    # Все видео сохраняем как MP4 для совместимости
    if instance.pk:
        filename_base = str(instance.pk)
    else:
        filename_base = f"temp_{uuid.uuid4().hex[:8]}"
    
    return os.path.join('videos/', f"{filename_base}.mp4")


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
        """Переопределяем сохранение для конвертации и создания превью"""
        is_new = self.pk is None
        
        # Сохраняем оригинальный формат до сохранения
        if self.video and hasattr(self.video, 'name'):
            ext = self.video.name.split('.')[-1].lower() if '.' in self.video.name else ''
            self.original_format = ext
        
        super().save(*args, **kwargs)
        
        # Конвертируем в MP4 если загружен не mp4 и это новое видео
        if is_new and self.video and self.original_format.lower() not in ['', 'mp4']:
            self.convert_to_mp4()
        
        # Создаём превью из видео (после первого сохранения)
        if is_new and self.video:
            self.create_thumbnail()
    
    def convert_to_mp4(self):
        """Конвертирует видео в формат MP4 (H.264) для совместимости"""
        if not self.video:
            return
        
        try:
            video_path = self.video.path
            if not os.path.exists(video_path):
                print(f"Видео файл не найден: {video_path}")
                return
            
            # Проверяем наличие ffmpeg
            if not shutil.which('ffmpeg'):
                print("FFmpeg не найден, пропускаем конвертацию")
                return
            
            # Формируем правильный путь для выходного файла
            ext = self.original_format.lower()
            input_path = video_path
            output_path = video_path.replace(f'.{ext}', '.mp4')
            
            # Если входной файл уже mp4, пропускаем
            if ext == 'mp4' and input_path == output_path:
                print(f"Видео #{self.pk} уже в формате MP4, конвертация не требуется")
                return
            
            # Если файл уже с расширением .mp4 в конце пути, но формат другой,
            # нужно создать временный файл
            if ext != 'mp4':
                temp_path = video_path.replace(f'.{ext}', '_temp.mp4')
                
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
                    temp_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(temp_path):
                    # Удаляем оригинальный файл
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    # Переименовываем temp в правильное имя
                    os.rename(temp_path, output_path)
                    
                    # Обновляем путь к файлу в базе
                    new_filename = os.path.basename(output_path)
                    self.video.name = os.path.join('videos/', new_filename)
                    super().save(update_fields=['video'])
                    
                    print(f"Видео #{self.pk} конвертировано в MP4")
                else:
                    print(f"Ошибка конвертации: {result.stderr}")
            else:
                print(f"Видео #{self.pk} уже MP4, пропускаем конвертацию")
                
        except Exception as e:
            print(f"Ошибка конвертации видео #{self.pk}: {e}")
    
    def create_thumbnail(self):
        """Создаёт превью из первого кадра видео"""
        if not self.video:
            return
        
        try:
            # Проверяем наличие ffmpeg
            if not shutil.which('ffmpeg'):
                print("FFmpeg не найден, превью не создано")
                return
            
            video_path = self.video.path
            
            # Проверяем существует ли файл
            if not os.path.exists(video_path):
                print(f"Видео файл не найден: {video_path}")
                return
            
            # Путь для сохранения превью
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_path = os.path.join(thumbnail_dir, f'{self.pk}.jpg')
            
            # Извлекаем первый кадр из видео
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-ss', '00:00:01',  # Берем кадр на 1-й секунде
                '-vframes', '1',
                '-vf', 'scale=480:-1',  # Ширина 480px, высота автоматически
                '-q:v', '2',  # Высокое качество JPEG
                thumbnail_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(thumbnail_path):
                # Открываем и оптимизируем изображение
                img = Image.open(thumbnail_path)
                img = img.convert('RGB')
                img.save(thumbnail_path, 'JPEG', quality=85)
                img.close()
                
                # Обновляем поле thumbnail
                with open(thumbnail_path, 'rb') as f:
                    self.thumbnail.save(f'{self.pk}.jpg', ContentFile(f.read()), save=True)
                
                print(f"Превью для видео #{self.pk} создано")
            else:
                print(f"Ошибка создания превью: {result.stderr}")
                
        except Exception as e:
            print(f"Ошибка создания превью для видео #{self.pk}: {e}")
    
    def generate_thumbnail_on_demand(self):
        """Создаёт превью по запросу (если отсутствует)"""
        # Проверяем, существует ли файл превью
        thumbnail_exists = False
        if self.thumbnail:
            try:
                thumbnail_exists = os.path.exists(self.thumbnail.path)
            except:
                pass
        
        if not thumbnail_exists:
            self.create_thumbnail()