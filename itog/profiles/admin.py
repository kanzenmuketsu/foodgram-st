from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile
from django.contrib import auth

UserAdmin.fieldsets += (
    ("Еще какие-то данные", {'fields': (
        'avatar',
        'cart',
        'bookmared',
        'followers'
    )}),
)
UserAdmin.filter_horizontal += ('cart', 'bookmared', 'followers')
admin.site.register(Profile, UserAdmin)
admin.site.unregister(auth.models.Group)
