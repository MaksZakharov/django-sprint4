from django.core.paginator import Paginator
from django.utils import timezone

from blog.models import Post


def paginate_queryset(request, queryset, per_page):
    """
    Возвращает объект страницы для пагинируемого запроса.

    Аргументы:
        request (HttpRequest): Объект запроса.
        queryset (QuerySet): Запрос к базе данных.
        per_page (int): Количество объектов на страницу.

    Возвращает:
        Page: Объект страницы с результатами пагинации.
    """
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_published_posts():
    """
    Возвращает базовый QuerySet опубликованных постов.

    Фильтрует только опубликованные посты с датой публикации
    не позже текущей и опубликованной категорией.

    Возвращает:
        QuerySet: Список подходящих постов.
    """
    return Post.objects.select_related(
        "category", "location", "author").filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
