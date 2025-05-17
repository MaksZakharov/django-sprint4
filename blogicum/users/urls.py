from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('<str:username>/', views.profile, name='profile'),
]
