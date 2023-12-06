# Generated by Django 3.2.16 on 2023-12-06 10:44

import django.core.validators
from django.db import migrations, models
import recipes.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='Время приготовления не может быть меньше 1 мин.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000), recipes.validators.validate_value_greater_zero], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(db_index=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000), recipes.validators.validate_value_greater_zero], verbose_name='Количество ингридиентов'),
        ),
    ]