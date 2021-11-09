import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
import sys

# Опредляем User как метод класса пользователя
User = get_user_model()


# Создаем класс Пост с полями Slug/Заголовок/Автор/Содержимое/Дата публикации/Картинка
class Post(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()                 # Текст
    pub_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='media/img', verbose_name='Картинки', blank=True)

    def __str__(self):
        # Необходимо для понятного отображения в админке сайта
        return self.title

    def save(self, *args, **kwargs):
        # Ниже написан модуль обрезки файла при сохранении до указанного разрешения 900х900
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')
        resized_new_img = new_img.resize((900, 578), Image.ANTIALIAS)
        filestream = BytesIO()
        resized_new_img.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        self.image = InMemoryUploadedFile(
        filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
        )
        super().save(*args, **kwargs)

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def get_absolute_url(self):
        # Необходимо для формирования ссылок на конкретный пост по уникальному slug
        return reverse('blog', kwargs={'slug': self.slug})


# Создаем класс Коммент с полями Пост/Автор/Содержимое/Дата публикации
class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Пост', on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE)
    text = models.CharField(max_length=300, verbose_name='Комментарий')
    data_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # Необходимо для понятного отображения в админке сайта
        return 'Комментарий - {} {} : {}'.format(self.author.first_name, self.author.last_name, self.text)