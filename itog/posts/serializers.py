from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField,
    ValidationError
)
from .models import Ingredient, Recipi, RecipiIngredientAmount
from drf_extra_fields.fields import Base64ImageField
from profiles.serializers import UserSerializer


class IngWithAmountSerializer(ModelSerializer):
    amount = SerializerMethodField()

    class Meta:
        model = RecipiIngredientAmount
        fields = ('amount',)

    def to_internal_value(self, data):
        try:
            name = Ingredient.objects.get(pk=data['id'])
        except Exception as e:
            raise ValidationError({'name': e})
        return {
            "name": name,
            "amount": data['amount']
        }

    def to_representation(self, data):
        return {
            'id': data.Ingredient.id,
            'name': data.Ingredient.name,
            'measurement_unit': data.Ingredient.measurement_unit,
            'amount': data.amount
        }

    def get_amount(self, data):
        for ing in self.context['request'].data['ingredients']:
            if ing['id'] == data.id:
                return ing['amount']
        return 1


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipiSerializer(ModelSerializer):
    image = Base64ImageField()
    ingredients = IngWithAmountSerializer(source='RRR', many=True)
    author = UserSerializer(read_only=True)
    bookmared = SerializerMethodField()
    cart = SerializerMethodField()

    class Meta:
        model = Recipi
        fields = (
            'id',
            'author',
            'ingredients',
            'bookmared',
            'cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('bookmared', 'cart', 'author')

    def _user(self, obj):
        request = self.context.get('request', None)
        if request:
            return request.user

    def get_cart(self, obj):
        user = self._user(self)
        return obj.cart.filter(pk=user.id).exists()

    def get_bookmared(self, obj):
        user = self._user(self)
        return obj.bookmared.filter(pk=user.id).exists()

    def create(self, validated_data):
        user = self.context['request'].user
        ingredients = validated_data.pop('RRR', False)
        recipi = Recipi.objects.create(**validated_data, author=user)

        for ing in ingredients:
            d = dict(ing)
            RecipiIngredientAmount.objects.create(
                recipi=recipi, Ingredient=d['name'], amount=d['amount']
            )

        return recipi

    def update(self, validated_data):
        return self.create(validated_data)
