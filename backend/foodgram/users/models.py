from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import validate_username


class User(AbstractUser):
    """Кастомная модель User"""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        )
    username = models.CharField(
        verbose_name='Пользователь',
        max_length=150,
        unique=True,
        help_text=(
            'Не больше 150 символов.'
            'Только буквы, цифры и @/./+/-/_'
        ),
        validators=[validate_username],
        error_messages={
            'unique': (
                'Пользователь с таким именем или'
                ' с таким емейлом уже существует'
            )
        }
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
        )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    """Модель подписчиков"""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта'
    )
    def __str__(self):
        return f'Пользователь "{self.subscriber}" подписан на "{self.author}"'

    class Meta:
        verbose_name = 'Подписка на пользователя'
        verbose_name_plural = 'Подписки на пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name="user_cannot_subscrib_himself",
            ),
        ]