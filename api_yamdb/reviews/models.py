import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'
    ROLE = [(USER_ROLE, 'user'),
            (MODERATOR_ROLE, 'moderator'),
            (ADMIN_ROLE, 'admin')]

    first_name = models.CharField(max_length=150,
                                  null=True, blank=True)
    last_name = models.CharField(max_length=150,
                                 null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE,
                            default=USER_ROLE, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ADMIN_ROLE or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR_ROLE


class ConfirmationCode(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='codes')
    code = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'code'],
                name='unique_user_code'
            )
        ]


class Genre(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0),
                    MaxValueValidator(datetime.datetime.now().year)],
        verbose_name='Год выпуска'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles', verbose_name='Жанр')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='titles',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['-pub_date']


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Комментарий')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        null=False,
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
