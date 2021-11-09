from django.urls import path
from .import views
from django.contrib.auth.views import LogoutView
from .views import (
                        base_list_view,
                        blog_list_view,
                        post_detail_view,
                        login_view,
                        registration_view,
                        profile_view,
                        delete_comment_view,
                        feedback_view,
                        )
urlpatterns = [
    path('', base_list_view.as_view(), name='base'),
    path('login/', login_view.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('registration/', registration_view.as_view(), name='registration'),
    path('blog/', blog_list_view.as_view(), name='blog'),
    path('blog/<str:slug>/', post_detail_view.as_view(), name='post'),
    path('profile/', profile_view.as_view(), name='profile'),
    path('delete_comment/<int:comment_id>/', delete_comment_view.as_view(), name='delete_comment'),
    path('feedback/', feedback_view.as_view(), name='feedback'),
]