from django.contrib.auth.models import AbstractUser
from django.db import models

from posts.models import Recipi


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
        null=False,
        unique=True
    )
    avatar = models.ImageField(
        'Аватарка',
        upload_to='profile_avatars',
        null=True,
        blank=True
    )
    bookmared = models.ManyToManyField(
        Recipi,
        related_name='bookmared',
        verbose_name='Избранное',
        blank=True
    )
    cart = models.ManyToManyField(
        Recipi,
        related_name='cart',
        verbose_name='Корзина',
        blank=True
    )
    followers = models.ManyToManyField(
        'self',
        related_name='flws',
        blank=True,
        symmetrical=False
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    def __str__(self):
        return self.username
