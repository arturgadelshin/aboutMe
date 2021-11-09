from django.contrib import admin
from .models import Post, Comment

# Здесь прописываются модели доступные в админке
admin.site.register(Post)
admin.site.register(Comment)

