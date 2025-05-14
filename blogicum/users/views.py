from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator


from django.contrib.auth import get_user_model
from blog.models import Post
from blog.constants import POSTS_PER_PAGE

User = get_user_model()

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-pub_date')
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'page_obj': page_obj,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})
