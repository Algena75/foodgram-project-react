import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True)
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True)

    class Meta:
        ordering = ('pk', )

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        if not re.match(r'[\w.@+-]+\Z', value):
            raise ValidationError(
                f'{value} содержит запрещённые символы.'
            )
        return value

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписавшийся пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный автор',
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self):
        return f'{self.user} --> {self.author}'
