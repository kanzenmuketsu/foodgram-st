from django.contrib.auth.models import AbstractUser
from django.db import models

from posts.models import Recepi


class Profile(AbstractUser):
    avatar = models.ImageField(
        'Аватарка',
        upload_to='profile_avatars',
        null=False,
        blank=False
    )
    favorite = models.ManyToManyField(
        Recepi,
        related_name='favorite',
        verbose_name='Избранное',
        blank=True
    )
    cart = models.ManyToManyField(
        Recepi,
        related_name='cart',
        verbose_name='Корзина',
        blank=True
    )

    def __str__(self):
        return self.username
