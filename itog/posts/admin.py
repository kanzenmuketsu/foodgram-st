from django.contrib import admin

from .models import Ingredient, Recepi


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


class RecepiAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    )
    readonly_fields = ('favorite_entries',)
    search_fields = ('name', 'author')
    filter_horizontal = ('ingredients',)

    @admin.display(description='Добавлено в избранное')
    def favorite_entries(self, obj):
        return obj.favorite.count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recepi, RecepiAdmin)
