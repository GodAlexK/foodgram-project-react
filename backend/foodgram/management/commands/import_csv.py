from csv import reader

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингридиентов в БД'

    def handle(self, *args, **options):
        print('Загрузка данных')

        print('*ingredients')
        PATH_CSV = 'management/commands/ingredients.csv'
        ingredients = []
        for row in reader(open(PATH_CSV)):
            ingredients.append(
                Ingredient(name=row[0], measurement_unit=row[1])
            )
        Ingredient.objects.bulk_create(ingredients)
