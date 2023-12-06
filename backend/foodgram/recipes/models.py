from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .validators import validate_slug, validate_value_greater_zero


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
        db_index=True,)
    color = ColorField(
        verbose_name='Цвет тега',)
    slug = models.SlugField(
        verbose_name='Метка',
        max_length=200,
        unique=True,
        validators=[validate_slug],)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags'),
        )


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=200)
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Hазвание рецепта',
        db_index=True)
    text = models.TextField(
        verbose_name='Описание рецепта')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1),
                    validate_value_greater_zero],
        verbose_name='Время приготовления',
        help_text='Время приготовления не может быть меньше 1 мин.')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Tags')
    favorites = models.ManyToManyField(
        User,
        related_name='favorites',
        verbose_name='Избранное',
        blank=True)
    shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        verbose_name='Список покупок',
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации рецепта',)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_ingredients')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1),
                    validate_value_greater_zero
                    ],
        verbose_name='Количество ингридиентов',
        db_index=True)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'

    class Meta:
        verbose_name = 'Количество ингридиентов'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients_in_recipes')
                ]
