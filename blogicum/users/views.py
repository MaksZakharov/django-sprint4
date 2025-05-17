from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from django.utils import timezone

from blog.constants import POSTS_PER_PAGE
from blog.models import Post
from blogicum.utils.service import paginate_queryset

User = get_user_model()


def profile(request, username):
    """
    Отображает страницу пользователя с его публикациями.

    Аргументы:
        request (HttpRequest): Объект запроса.
        username (str): Имя пользователя.

    Возвращает:
        HttpResponse: HTML-страница профиля пользователя с пагинацией.
    """
    user = get_object_or_404(User, username=username)

    if request.user == user:
        posts = Post.objects.filter(author=user)
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lte=timezone.now()
        )

    posts = (
        posts.
        annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    page_obj = paginate_queryset(request, posts, POSTS_PER_PAGE)

    return render(request, 'users/profile.html', {
        'profile_user': user,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request):
    """
    Отображает и обрабатывает форму редактирования профиля.

    Аргументы:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Страница с формой редактирования или редирект на профиль.
    """
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})
