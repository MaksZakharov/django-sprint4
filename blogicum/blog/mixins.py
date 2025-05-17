from django.shortcuts import get_object_or_404, redirect
from blog.models import Post


class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get("post_id"))
        if request.user != post.author:
            return redirect('blog:post_detail', post_id=post.pk)
        return super().dispatch(request, *args, **kwargs)
