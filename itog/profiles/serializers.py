from djoser.serializers import UserCreateSerializer \
    as BaseUserRegistrationSerializer
from rest_framework import serializers


class UserSerializer(BaseUserRegistrationSerializer):
    is_subsribed = serializers.SerializerMethodField()

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'cart',
            'is_subsribed'
        )

    def get_is_subsribed(self, obj):
        user = self._user(self)
        if obj == user:
            return False
        return obj.flws.filter(pk=user.id).exists()

    def _user(self, obj):
        request = self.context.get('request', None)
        if request:
            return request.user
