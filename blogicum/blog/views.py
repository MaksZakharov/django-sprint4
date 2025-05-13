from django.shortcuts import get_object_or_404, render
from django.utils import timezone

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
