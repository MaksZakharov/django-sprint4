from django.shortcuts import redirect
from django.urls import reverse

from blog.models import Comment


class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user != post.author:
            return redirect('blog:post_detail', post_id=post.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentAccessMixin:
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
