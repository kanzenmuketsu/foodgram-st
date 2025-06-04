from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField,
    ValidationError, StringRelatedField, IntegerField
)
from .models import Ingredient, Recipi, RecipiIngredientAmount
from drf_extra_fields.fields import Base64ImageField
from profiles.serializers import UserSerializer
from itog.settings import MIN_AMOUNT_FOR_RECIPI, MAX_AMOUNT_FOR_RECIPI


class IngWithAmountSerializer(ModelSerializer):
    amount = IntegerField(
        max_value=MAX_AMOUNT_FOR_RECIPI, min_value=MIN_AMOUNT_FOR_RECIPI
    )

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


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipiSerializer(ModelSerializer):
    image = Base64ImageField()
    ingredients = IngWithAmountSerializer(
        source='ingredientsWTamount', many=True
    )
    author = UserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipi
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('is_favorited', 'is_in_shopping_cart', 'author')

    def _user(self, obj):
        request = self.context.get('request', None)
        if request:
            return request.user

    def get_is_in_shopping_cart(self, obj):
        user = self._user(self)
        return obj.cart.filter(pk=user.id).exists()

    def get_is_favorited(self, obj):
        user = self._user(self)
        return obj.bookmared.filter(pk=user.id).exists()

    def create(self, validated_data):
        user = self.context['request'].user
        ingredients = validated_data.pop('ingredientsWTamount', False)
        if not ingredients:
            raise ValidationError({'error': 'нужны ингредиенты'})

        recipi = Recipi.objects.create(**validated_data, author=user)

        self.add_ingredients(recipi=recipi, ingredients=ingredients)

        return recipi

    def update(self, obj, validated_data):
        user = self.context['request'].user
        if not obj.author == user:
            raise ValidationError({'author': 'Вы не автор'})
        ingredients = validated_data.pop('ingredientsWTamount', False)
        if not ingredients:
            raise ValidationError({'ingredients': 'нужны ингредиенты'})

        Recipi.objects.filter(pk=obj.id).update(**validated_data)
        obj.ingredients.clear()

        self.add_ingredients(recipi=obj, ingredients=ingredients)

        return obj

    def add_ingredients(self, recipi, ingredients):
        to_create = []
        for ing in ingredients:
            to_create.append(RecipiIngredientAmount(
                recipi=recipi, Ingredient=ing['name'], amount=ing['amount']
            ))
        RecipiIngredientAmount.objects.bulk_create(to_create)

    def validate(self, data):
        ingredients = data.get('ingredientsWTamount', False)
        if not ingredients:
            raise ValidationError({'ingredients': 'нужны ингредиенты'})

        ings = set()
        for i in ingredients:
            if i['name'] in ings:
                raise ValidationError(
                    {'ingredients': 'ингредиенты не должны повторяться'}
                )
            ings.add(i['name'])
        return data


class RecipiShortLinkSerializer(ModelSerializer):
    short_link = StringRelatedField()

    class Meta:
        model = Recipi
        fields = (
            'short_link',
        )
        read_only_fields = ('short_link',)


class RecipiShortSerializer(RecipiSerializer):
    class Meta(RecipiSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')
