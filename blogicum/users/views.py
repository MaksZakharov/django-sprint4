from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from blog.service import get_published_posts, paginate_queryset

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

    base_queryset = user.posts.all()

    post_list = get_published_posts(
        base_queryset=base_queryset,
        filter_published=request.user != user
    )

    page_obj = paginate_queryset(request, post_list)

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
    form = UserChangeForm(request.POST or None, instance=request.user)

    if form.is_valid():
        form.save()
        return redirect('users:profile', username=request.user.username)

    return render(request, 'users/edit_profile.html', {'form': form})
