from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm

from .constants import POSTS_PER_PAGE
from .models import Category, Post


def get_published_posts():
    """
    Возвращает базовый queryset для опубликованных постов.

    Фильтрует посты, удовлетворяющие следующим условиям:
    - is_published=True
    - pub_date не позже текущего времени
    - категория is_published=True

    Возвращает:
        QuerySet: Отфильтрованные посты, удовлетворяющие указанным условиям.
    """
    return Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def index(request):
    """
    Отображает главную страницу блога.

    Возвращает список из 5 последних опубликованных постов,
    у которых:
    - is_published=True,
    - pub_date не позже текущего времени,
    - категория также опубликована.

    Аргументы:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: HTML-страница с последними постами.
    """
    post_list = get_published_posts().order_by('-pub_date')[:POSTS_PER_PAGE]
    return render(request, 'blog/index.html', {'post_list': post_list})


def post_detail(request, post_id):
    """
    Отображает страницу с подробной информацией о посте.

    Пост должен соответствовать условиям:
    - is_published=True,
    - pub_date не позже текущего времени,
    - категория также опубликована.

    Аргументы:
        request (HttpRequest): Объект запроса.
        post_id (int): Идентификатор поста.

    Возвращает:
        HttpResponse: HTML-страница с подробным содержанием поста.
        Http404: Если пост не найден или не соответствует условиям.
    """
    post = get_object_or_404(
        get_published_posts(),
        id=post_id
    )
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    """
    Отображает страницу постов в выбранной категории.

    Отображаются только опубликованные посты и категория, если:
    - категория is_published=True,
    - пост is_published=True,
    - pub_date не позже текущего времени.

    Аргументы:
        request (HttpRequest): Объект запроса.
        category_slug (str): Слаг категории.

    Возвращает:
        HttpResponse: HTML-страница с постами из категории.
        Http404: Если категория не найдена или не опубликована.
    """
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_published_posts().filter(
        category=category
    ).order_by('-pub_date')
    return render(
        request,
        'blog/category.html',
        {'category': category, 'post_list': post_list}
    )


def csrf_failure(request, reason=''):
    """
    Обрабатывает ошибку CSRF-токена (403 Forbidden).

    Отображает кастомную страницу для случаев:
    - Недействительного CSRF-токена
    - Отсутствия CSRF-токена в запросе

    Аргументы:
        request (HttpRequest): Объект запроса.
        reason (str): Причина ошибки (опционально).

    Возвращает:
        HttpResponse: HTML-страница 403csrf.html с кодом статуса 403.
    """
    return render(request, 'pages/403csrf.html', status=403)

def page_not_found(request, exception):
    """
    Обрабатывает ошибку "Страница не найдена" (404 Not Found).

    Отображает кастомную страницу для случаев:
    - Несуществующих URL
    - Доступа к неопубликованным ресурсам

    Аргументы:
        request (HttpRequest): Объект запроса.
        exception (Exception): Исключение, вызвавшее ошибку.

    Возвращает:
        HttpResponse: HTML-страница 404.html с кодом статуса 404.
    """
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """
    Обрабатывает внутренние ошибки сервера (500 Internal Server Error).

    Отображает кастомную страницу при:
    - Необработанных исключениях
    - Критических ошибках в коде

    Аргументы:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: HTML-страница 500.html с кодом статуса 500.
    """
    return render(request, 'pages/500.html', status=500)

def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})

