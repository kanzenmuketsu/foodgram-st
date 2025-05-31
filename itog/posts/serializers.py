from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField,
    ValidationError, StringRelatedField
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
        raise ValidationError('error')

    def validate(self, data):
        if data['amount'] < 1:
            raise ValidationError(
                {'error': 'Количество ингредиента должна быть больше 1'}
            )
        return data


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
        print(validated_data)
        ingredients = validated_data.pop('RRR', False)
        print(ingredients)
        if not ingredients:
            raise ValidationError({'error': 'нужны ингредиенты'})

        recipi = Recipi.objects.create(**validated_data, author=user)

        for ing in ingredients:
            d = dict(ing)
            RecipiIngredientAmount.objects.create(
                recipi=recipi, Ingredient=d['name'], amount=d['amount']
            )

        return recipi

    def update(self, obj, validated_data):
        user = self.context['request'].user
        if not obj.author == user:
            raise ValidationError({'author': 'Вы не автор'})
        ingredients = validated_data.pop('RRR', False)
        if not ingredients:
            raise ValidationError({'ingredients': 'нужны ингредиенты'})

        recipi = Recipi.objects.update(**validated_data)
        obj = Recipi.objects.get(pk=recipi)
        obj.ingredients.clear()

        for ing in ingredients:
            d = dict(ing)
            RecipiIngredientAmount.objects.create(
                recipi=obj, Ingredient=d['name'], amount=d['amount']
            )

        return obj

    def validate(self, data):
        ings = set()
        ingredients = data.get('RRR', False)
        if not ingredients:
            raise ValidationError({'ingredients': 'нужны ингредиенты'})

        for i in ingredients:
            if i['name'] not in ings:
                ings.add(i['name'])
            else:
                raise ValidationError(
                    {'ingredients': 'ингредиенты не должны повторяться'}
                )
        if not data['image']:
            raise ValidationError(
                {'image': 'пустое фото'}
            )
        if data['cooking_time'] < 1:
            raise ValidationError(
                {'cooking_time': 'Время готовки не может быть меньше 1 мин'}
            )
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
        fields = ('name', 'image', 'cooking_time')
