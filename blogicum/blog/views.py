from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from .constants import POSTS_PER_PAGE
from .models import Category, Post, Comment
from .forms import PostForm, CommentForm


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
    post_list = get_published_posts().order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


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
def post_detail(request, post_id):
    post = get_object_or_404(get_published_posts(), id=post_id)
    form = CommentForm()  # ← создаём пустую форму
    comments = post.comments.all()  # ← если хочешь отдельно использовать
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,  # ← обязательно передаём форму в шаблон
        'comments': comments,
    })    


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

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
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

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('users:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.pk})

    def test_func(self):
        return self.request.user == self.get_object().author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        return self.request.user == self.get_object().author

@require_POST
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.post.id})

    def test_func(self):
        return self.request.user == self.get_object().author

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if request.user != comment.author:
        raise PermissionDenied  # Запретить удаление чужих комментариев

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment,
        'post': comment.post
    })
