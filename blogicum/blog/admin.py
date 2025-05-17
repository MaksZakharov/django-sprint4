from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'is_published')
    list_filter = ('is_published', 'category', 'location', 'author')
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass
