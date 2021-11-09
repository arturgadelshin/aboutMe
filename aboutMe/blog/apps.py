from django.apps import AppConfig

# Здесь прописываются все приложения подключенные к проекту


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
