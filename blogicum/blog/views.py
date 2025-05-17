from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView
from django.views.generic.edit import UpdateView
from django.views.decorators.csrf import requires_csrf_token
from django.db.models import Count

from .constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


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


def index(request):
    """
    Отображает главную страницу со списком постов.

    Аргументы:
        request (HttpRequest): Текущий запрос.

    Возвращает:
        HttpResponse: Список постов с пагинацией.
    """
    post_list = get_published_posts().annotate(
    comment_count=Count('comments')
    ).order_by("-pub_date")
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, post_id):
    """
    Отображает страницу с подробностями поста.

    Аргументы:
        request (HttpRequest): Текущий запрос.
        post_id (int): ID поста.

    Возвращает:
        HttpResponse: Страница поста с комментариями и формой.
    """
    post = get_object_or_404(get_published_posts(), id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    return render(
        request,
        "blog/detail.html",
        {
            "post": post,
            "form": form,
            "comments": comments,
        },
    )


def category_posts(request, category_slug):
    """
    Отображает страницу постов по категории.

    Аргументы:
        request (HttpRequest): Текущий запрос.
        category_slug (str): Слаг категории.

    Возвращает:
        HttpResponse: Страница с постами данной категории.
    """
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = (
        get_published_posts()
        .filter(category=category).
        order_by("-pub_date")
    )
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj}
    )


@requires_csrf_token
def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)

def registration(request):
    """
    Регистрация нового пользователя.

    Аргументы:
        request (HttpRequest): Текущий запрос.

    Возвращает:
        HttpResponse: Страница с формой регистрации.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(
        request,
        "registration/registration_form.html",
        {"form": form}
    )


@login_required
def create_post(request):
    """
    Создание нового поста авторизованным пользователем.

    Аргументы:
        request (HttpRequest): Текущий запрос.

    Возвращает:
        HttpResponse: Страница с формой создания поста или редирект.
    """
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("users:profile", username=request.user.username)
    else:
        form = PostForm()
    return render(request, "blog/create.html", {"form": form})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def get_success_url(self):

        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.pk}
        )

    def test_func(self):

        return self.request.user == self.get_object().author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")

    def test_func(self):

        return self.request.user == self.get_object().author


@require_POST
@login_required
def add_comment(request, post_id):
    """
    Добавление комментария к посту.

    Аргументы:
        request (HttpRequest): Текущий запрос.
        post_id (int): ID поста.

    Возвращает:
        HttpResponse: Редирект на страницу поста.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("blog:post_detail", post_id=post_id)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"

    def get_success_url(self):

        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.post.id}
        )

    def test_func(self):

        return self.request.user == self.get_object().author


@login_required
def delete_comment(request, post_id, comment_id):
    """
    Удаление комментария (только автор).

    Аргументы:
        request (HttpRequest): Текущий запрос.
        post_id (int): ID поста.
        comment_id (int): ID комментария.

    Возвращает:
        HttpResponse: Подтверждение удаления или редирект.
    """
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if request.user != comment.author:
        raise PermissionDenied

    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)

    return render(request, "blog/comment.html", {
        "comment": comment,
        "post": comment.post,
    })
