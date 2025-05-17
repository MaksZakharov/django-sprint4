from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView
from django.views.generic.edit import UpdateView

from blogicum.utils.service import get_published_posts, paginate_queryset
from .constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


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
    page_obj = paginate_queryset(request, post_list, POSTS_PER_PAGE)
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
    post = get_object_or_404(
        Post.objects.select_related("category", "location", "author"),
        id=post_id
    )

    if (
        not post.is_published
        or post.pub_date > timezone.now()
        or not post.category.is_published
    ):
        if request.user != post.author:
            raise Http404()

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
    page_obj = paginate_queryset(request, post_list, POSTS_PER_PAGE)
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


class PostUpdateView(UpdateView):

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if not request.user.is_authenticated:
            return redirect('blog:post_detail', post_id=post.pk)
        if request.user != post.author:
            return redirect('blog:post_detail', post_id=post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.pk}
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("blog:post_detail", post_id=self.kwargs["post_id"])
        raise PermissionDenied


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Post
    pk_url_kwarg = 'post_id'
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
    pk_url_kwarg = "comment_id"

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"post_id": self.object.post.id}
        )

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        raise Http404()


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"
    http_method_names = ['get', 'post']

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.object.post.id})

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.get_object()
        return context
