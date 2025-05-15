from django.urls import path
from .views import PostUpdateView
from .views import PostDeleteView

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts',
    ),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path(
    'posts/<int:post_id>/edit_comment/<int:pk>/',
    views.CommentUpdateView.as_view(),
    name='edit_comment'
    ),
    path(
    'posts/<int:post_id>/delete_comment/<int:comment_id>/',
    views.delete_comment,
    name='delete_comment',
    ),
]
