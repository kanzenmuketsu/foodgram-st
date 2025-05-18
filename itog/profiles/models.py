from django.contrib.auth.models import AbstractUser
from django.db import models

from posts.models import Recepi


class Profile(AbstractUser):
    first_name = models.CharField(
        max_length=30,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=30,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=64,
        blank=False,
        null=False
    )
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
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    def __str__(self):
        return self.username
