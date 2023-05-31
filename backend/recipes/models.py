import re

from django.core.exceptions import ValidationError
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Тэг',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text='Адрес'
    )

    def __str__(self):
        return self.name[:15]

    def validate_slug(self, value):
        if not re.match(r'^[-a-zA-Z0-9_]+$', value):
            raise ValidationError(
                "Поле slug содержит запрещенные символы"
            )
        return value


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Наименование',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name[:30]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Наименование'
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='recipes/images/',
        default=None,
        null=False
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
        null=False
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах'
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name[:30]

    class Meta:
        ordering = ('-created', 'author')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.IntegerField(
        verbose_name='Количество в граммах',
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='Рецепт в корзине',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buyer',
        verbose_name='Покупатель',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_shoppingcart',
            ),
        ]

    def __str__(self):
        return (
            f'{self.user} --> {self.recipe.name}'
        )


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_selected',
        verbose_name='Избранный рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='selector',
        verbose_name='Выбирающий пользователь',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        return (
            f'{self.user} --> {self.recipe.name}'
        )
