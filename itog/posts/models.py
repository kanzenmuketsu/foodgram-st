from django.conf import settings
from django.db import models
from itog.settings import BASE_URL_SITE, SHORT_LINK_URL


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Наименование', max_length=128, unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения', max_length=32
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipiIngredientAmount(models.Model):
    recipi = models.ForeignKey(
        'Recipi',
        on_delete=models.CASCADE,
        related_name='ingredientsWTamount'
    )
    Ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipi", "Ingredient"], name="unique_Ing_recipi"
            )
        ]


class ShortUrl(models.Model):
    short_link = models.CharField(
        verbose_name='Ссылка',
        null=True,
        blank=True,
        default=None
    )

    def __str__(self):
        return f'{BASE_URL_SITE}{SHORT_LINK_URL}{self.short_link}'


class Recipi(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipi_author'
    )
    name = models.CharField(
        verbose_name='Название рецепта', max_length=128
    )
    image = models.ImageField(
        'Фото',
        upload_to='recipi_images',
        blank=False,
        null=False
    )
    text = models.TextField(
        verbose_name='Описание', max_length=255
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        through='RecipiIngredientAmount'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text="(в минутах)"
    )
    short_link = models.OneToOneField(
        ShortUrl,
        verbose_name='Короткая ссылка',
        related_name='shortlink',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
