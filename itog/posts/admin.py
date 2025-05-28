from django.contrib import admin

from .models import Ingredient, Recipi, RecipiIngredientAmount


class RecipiIngredientAmountInline(admin.TabularInline):
    model = RecipiIngredientAmount
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


class RecipiAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    )
    inlines = [RecipiIngredientAmountInline]
    readonly_fields = ('favorite_entries',)
    search_fields = ('name', 'author')

    @admin.display(description='Добавлено в избранное')
    def favorite_entries(self, obj):
        return obj.favorite.count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipi, RecipiAdmin)
