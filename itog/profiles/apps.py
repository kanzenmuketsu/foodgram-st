from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'
    verbose_name = 'Пользователи'

    def ready(self):
        from djoser.serializers import UserSerializer
        from djoser.conf import default_settings

        UserSerializer.Meta.fields += 'avatar',
        default_settings['PERMISSIONS']['user'] = ["rest_framework.permissions.IsAuthenticatedOrReadOnly"]
        default_settings['PERMISSIONS']['user_list'] = ["rest_framework.permissions.IsAuthenticatedOrReadOnly"]

        from djoser.views import UserViewSet
        UserViewSet.get_queryset = get_queryset


def get_queryset(self):
    return self.queryset
