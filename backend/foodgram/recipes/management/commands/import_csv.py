import csv

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILES
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из CSV в БД"""

    help = 'Загрузка ингредиентов в БД'

    def handle(self, *args, **kwargs):
        with open(
                f'{CSV_FILES}/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            ingredients = [
                Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
        print('Ингредиенты загружены')
        print('ADD', Ingredient.objects.count(), 'Ingredient')
