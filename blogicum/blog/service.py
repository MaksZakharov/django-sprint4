from django.core.paginator import Paginator
from django.db.models import Count
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


def get_published_posts(
    count_comments=True,
    order_by_date=True,
    base_queryset=None,
    filter_published=True,
):
    """
    Возвращает QuerySet опубликованных постов.

    Аргументы:
        count_comments (bool): Добавлять аннотацию с количеством комментариев.
        order_by_date (bool): Сортировать ли по убыванию даты публикации.
        base_queryset (QuerySet): Начальный QuerySet.

    Возвращает:
        QuerySet: Посты, опубликованные, с категорией и без отложек.
    """
    queryset = base_queryset or Post.objects.all()

    queryset = queryset.select_related(
        "category",
        "location",
        "author"
    )

    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    if count_comments:
        queryset = queryset.annotate(comment_count=Count("comments"))

    if order_by_date:
        queryset = queryset.order_by("-pub_date")

    return queryset
