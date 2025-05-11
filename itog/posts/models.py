from django.conf import settings
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Наименование', max_length=128, unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения', max_length=32
    )

    class Meta:
        verbose_name = 'инградиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recepi(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта', max_length=128
    )
    image = models.ImageField(
        'Фото',
        upload_to='recepi_images'
    )
    text = models.TextField(
        verbose_name='Описание', max_length=255
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text="(в минутах)"
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
