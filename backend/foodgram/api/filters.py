from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    AllValuesMultipleFilter,
    BooleanFilter,
    CharFilter,
    ModelChoiceFilter
)

from django_filters import rest_framework as filters

from django.db import models
from django_filters import FilterSet, CharFilter

from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientSearchFilter(filters.FilterSet):
    """Фильтр поиска по названию ингредиента."""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )

    
class RecipeSearchFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug',)
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart=self.request.user)
        return queryset
