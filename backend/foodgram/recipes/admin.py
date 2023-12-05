from django.contrib import admin

from recipes import models


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count', )
    list_filter = ('name', 'author', 'tags',)

    def favorites_count(self, obj):
        return obj.favorites.count()


admin.site.register(models.Recipe, RecipeAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Tag)
admin.site.register(models.RecipeIngredient)
