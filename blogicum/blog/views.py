from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView
from django.views.generic.edit import UpdateView

from blog.constants import POSTS_PER_PAGE
from blog.forms import CommentForm, PostForm
from blog.mixins import AuthorRequiredMixin
from blog.models import Category, Comment, Post
from blog.service import get_published_posts, paginate_queryset


def index(request):
    """
    Отображает главную страницу со списком постов.

    Аргументы:
        request (HttpRequest): Текущий запрос.

    Возвращает:
        HttpResponse: Список постов с пагинацией.
    """
    post_list = get_published_posts()
    page_obj = paginate_queryset(request, post_list)
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
    comments = post.comments.select_related('author').all()
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
    base_queryset = category.posts.all()

    post_list = get_published_posts(
        count_comments=True,
        order_by_date=True,
        base_queryset=base_queryset
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
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("login")
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
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("users:profile", username=request.user.username)
    return render(request, "blog/create.html", {"form": form})


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.object.pk}
        )


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.get_object())
        return context


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
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("blog:post_detail", post_id=post_id)


class CommentUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "comment_id"
    template_name = "blog/comment.html"

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.object.post.id}
        )

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect("blog:post_detail", post_id=self.get_object().post.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.get_object()
        return context


class CommentDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/comment.html"

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.object.post.id}
        )

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect("blog:post_detail", post_id=self.get_object().post.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.get_object()
        return context
