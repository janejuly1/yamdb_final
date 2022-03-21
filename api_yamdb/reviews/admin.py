from django.contrib import admin

from .models import Category, Genre, Title, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'bio',
        'role',
    )
    list_filter = ('is_staff', 'is_superuser')


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'category',
        'author',
        'pub_date',
    )
    search_fields = ('name',)
    list_editable = ('category', )
    list_filter = ('pub_date', 'category', )


class CategoryGenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryGenreAdmin)
admin.site.register(Genre, CategoryGenreAdmin)
