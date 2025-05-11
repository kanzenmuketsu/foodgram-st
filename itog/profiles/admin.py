from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile

UserAdmin.fieldsets += (
    # Добавляем кортеж, где первый элемент — это название раздела в админке,
    # а второй элемент — словарь, где под ключом fields можно указать нужные поля.
    ("Еще какие-то данные", {'fields': ('avatar', 'cart', 'favorite')}),
)
UserAdmin.filter_horizontal += ('cart', 'favorite')
UserAdmin.list_display = ('username', 'email', 'is_staff', 'date_joined')
admin.site.register(Profile, UserAdmin)
