from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler403, handler404, handler500

handler403 = 'blog.views.csrf_failure'  # Для кастомной 403 (CSRF)
handler404 = 'blog.views.page_not_found'  # Для кастомной 404
handler500 = 'blog.views.server_error'  # Для кастомной 500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('', include('blog.urls')),
]
