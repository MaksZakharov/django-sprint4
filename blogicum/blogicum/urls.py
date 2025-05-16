from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500
from blog import views
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'blog.views.page_not_found'
handler500 = 'blog.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('', include('blog.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', views.registration, name='registration'),
    path('profile/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
