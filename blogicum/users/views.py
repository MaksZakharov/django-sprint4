from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from blog.models import Post  # если модель постов находится в blog

User = get_user_model()

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-pub_date')
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'posts': posts,
    })
