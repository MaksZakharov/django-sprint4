from django.core.paginator import Paginator


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
