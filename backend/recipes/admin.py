from django.contrib import admin
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class IngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'show_favorite')
    readonly_fields = ('show_favorite',)
    search_fields = ('text', 'name', )
    list_filter = ('author', 'name', 'tags')
    inlines = [IngredientsInLine]

    def show_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    show_favorite.short_description = 'Добавлен в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
