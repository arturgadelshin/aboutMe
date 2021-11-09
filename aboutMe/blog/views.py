import datetime
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Post, Comment
from django.views.generic import ListView, DetailView, View
from .forms import LoginForm, RegistrationForm, CommentForm, FeedbackForm
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.contrib import messages
from django.core.mail import BadHeaderError, send_mail, EmailMessage
from django.contrib.auth import get_user_model
User = get_user_model()


# Отображение главной страницы сайта
class base_list_view(ListView):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'base.html', context)


# Отображение постов из БД на странице блога
class blog_list_view(ListView, View):

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all
        context = {
           'posts': posts,
        }
        return render(request, 'blog.html', context)


# Отображение конкретных постов со связанными с ними комментариями и формы для нового комментария
class post_detail_view(DetailView):

    def get(self, request, slug, *args, **kwargs):
        post = Post.objects.get(slug=slug)
        comment = Comment.objects.filter(data_created__lte=timezone.now()).order_by('data_created')
        form = CommentForm(request.POST or None)
        context = {
            'form': form,
            'post': post,
            'comment': comment,
        }
        return render(request, 'post.html', context)

    # метод для нового комментария в БД
    def post(self, request, slug, *args, **kwargs):
        form = CommentForm(request.POST or None)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = Post.objects.get(slug=slug)
            new_comment.save()
            return HttpResponseRedirect(request.path_info)
        context = {'form': form, }
        return render(request, 'post.html', context)


# Отображение страницы авторизация
class login_view(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form}
        return render(request, 'login.html', context)

    # Метод для отправки данных их формы в БД, проверки и входа на сайт
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'login.html', context)


# Отображение страницы регистрации нового пользователя
class registration_view(View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {'form': form}
        return render(request, 'registration.html', context)

    # Метод для регистрации нового пользователя в БД
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.password = form.cleaned_data['password']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            # Отправка сообщения на @mail указанный при регистрации об успешной регистрации на сайте
            subject = 'Регистрация на сайте www.arturgadelshin.ru'
            message = f"Уважаемый пользователь {new_user.first_name} {new_user.last_name}, Вы успешно прошли регистрацию на сайте:www.arturgadelshin.ru"
            send_mail(subject, message, None, [new_user.email])
            messages.add_message(request, messages.INFO, f'{new_user.first_name} {new_user.last_name}, Вы успешно прошли регистрацию, перейти на сайт https://www.arturgadelshin.ru')
            return HttpResponseRedirect('/profile/')
        context = {'form': form, }
        return render(request, 'registration.html', context)


# Отображение страницы аутентифицированного пользователя с его комментариями к постам
class profile_view(ListView):

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        comments = Comment.objects.filter(author=request.user)
        context = {
            'comments': comments,
            'posts': posts,
        }
        return render(request, 'profile.html', context)


# Данный класс удаляет комментарий аутентифицированного пользователя из поста
class delete_comment_view(DetailView):

    def get(self, request, **kwargs):
        id_comment = kwargs.get('comment_id')
        comment = Comment.objects.get(id=id_comment)
        comment.delete()
        messages.add_message(request, messages.INFO, 'Комментарий успешно удален')
        return HttpResponseRedirect('/profile/')


# Отображение страницы обратной связи с администратором сайта
class feedback_view(View):

    def get(self, request, *args, **kwargs):
        form = FeedbackForm(request.POST or None)
        context = {'form': form}
        return render(request, 'feedback.html', context)

    # Метод проверки формы и отправки информации на @mail администратора с вопросом пользователя сайта
    def post(self, request, *args, **kwargs):
        form = FeedbackForm(request.POST or None)
        if form.is_valid():
            msg = form.cleaned_data['message']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            subject = 'Сообщение с сайта www.arturgadelshin.ru'
            message = f"Вам сообщение от: {first_name} {last_name} \nЭл.почта :{email}. \nТекст сообщения:{msg}"
            send_mail(subject, message, email, ['arturgadelshin@gmail.com'])
            messages.add_message(request, messages.INFO, 'Ваше сообщение успешно отправлено')
            return HttpResponseRedirect('/')
        return HttpResponse('Пожалуйста заполните все поля обозначенные *')