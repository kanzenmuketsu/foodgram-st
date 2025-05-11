from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Наименование', max_length=128
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения', max_length=32
    )

    class Meta:
        verbose_name = 'инградиент'
        verbose_name_plural = 'Инградиенты'

    def __str__(self):
        return self.name


class Recepi(models.Model):
    author = models.ForeignKey(
        User,
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
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Список ингредиентов'
    )
    cooking_time = models.PositiveIntegerField()
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Profile(User):
    avatar = models.ImageField(
        'Аватарка',
        upload_to='profile_avatars'
    )
    favorite = models.ForeignKey(
        Recepi,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Избранное'
    )
    cart = models.ForeignKey(
        Recepi,
        related_name='cart',
        on_delete=models.CASCADE,
        verbose_name='Корзина'
    )
