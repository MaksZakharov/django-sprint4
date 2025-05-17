from django.views.generic import TemplateView
from django.shortcuts import render


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """
    Обработка ошибки 404.

    Аргументы:
        request (HttpRequest): Текущий запрос.
        exception (Exception): Объект исключения.

    Возвращает:
        HttpResponse: Кастомная страница 404.
    """
    return render(request, "pages/404.html", status=404)


def server_error(request):
    """
    Обработка ошибки 500.

    Аргументы:
        request (HttpRequest): Текущий запрос.

    Возвращает:
        HttpResponse: Кастомная страница 500.
    """
    return render(request, "pages/500.html", status=500)


def permission_denied(request, exception):
    """
    Обработка ошибки 403.

    Аргументы:
        request (HttpRequest): Текущий запрос.
        exception (Exception): Объект исключения.

    Возвращает:
        HttpResponse: Кастомная страница 403.
    """
    if getattr(exception, 'reason', '') == 'CSRF':
        return render(request, "pages/403csrf.html", status=403)
    return render(request, "pages/403.html", status=403)
