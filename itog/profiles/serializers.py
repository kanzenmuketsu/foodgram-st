from djoser.serializers import UserSerializer \
    as BaseUserRegistrationSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField


class UserSerializer(BaseUserRegistrationSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if obj == user:
            return False
        return obj.followers.filter(pk=user.id).exists()
