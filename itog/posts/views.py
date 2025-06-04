from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView

from .models import Ingredient, Recipi, ShortUrl
from .permissions import AuthorOrReadOnly

from .serializers import (
    IngredientSerializer, RecipiSerializer,
    RecipiShortLinkSerializer, RecipiShortSerializer
)

from django.shortcuts import get_object_or_404, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
import uuid


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name', False)
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return Ingredient.objects.all()


class RecipiViewSet(ModelViewSet):
    serializer_class = RecipiSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        qset = Recipi.objects.all().order_by('-id')
        pk = self.request.query_params.get('author', False)
        bookmared = self.request.query_params.get('is_favorited', False)
        cart = self.request.query_params.get('is_in_shopping_cart', False)

        user = self.request.user
        if pk:
            qset = qset.filter(author=pk)
        if not user.is_anonymous:
            if bookmared:
                qset = qset.filter(bookmared__exact=user.id)
            if cart:
                qset = qset.filter(cart__exact=user.id)
        elif cart or bookmared:
            qset = []
        return qset

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = RecipiShortLinkSerializer(
            obj, data=request.data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        try:
            link = obj.short_link
        except Exception:
            link = False
        if link:
            return Response(
                {'short-link': obj.short_link.__str__()},
                status=status.HTTP_200_OK
            )
        else:
            short_link = uuid.uuid4().hex[:4]
            obj.short_link = ShortUrl.objects.create(short_link=short_link)
            obj.save()
            return Response(
                {'short-link': obj.short_link.__str__()},
                status=status.HTTP_200_OK
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = RecipiShortSerializer(obj)
        bookmared = request.user.bookmared
        already_bookmared = bookmared.filter(pk=obj.id).exists()

        if request.method == 'POST':
            if already_bookmared:
                return Response(
                    {"recipi": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            bookmared.add(obj)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not already_bookmared:
            return Response(
                {"recipi": "Рецепт не в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )

        bookmared.remove(obj)
        return Response(
            serializer.data,
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = RecipiShortSerializer(obj)
        cart = request.user.cart
        alreay_in_cart = cart.filter(pk=obj.id).exists()

        if request.method == 'POST':
            if alreay_in_cart:
                return Response(
                    {"recipi": "Рецепт уже в корзине"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart.add(obj)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not alreay_in_cart:
            return Response(
                {"recipi": "Рецепт не в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.remove(obj)
        return Response(
            serializer.data,
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        cart = request.user.cart.all()
        if not cart:
            return Response(
                {"cart": "Корзина пуста"},
                status=status.HTTP_400_BAD_REQUEST
            )
        ings = {}
        for recipi in cart:
            for ing_dict in recipi.ingredientsWTamount.all():
                ing, amount = ing_dict.Ingredient.name, ing_dict.amount
                unit = ing_dict.Ingredient.measurement_unit
                if ing not in ings:
                    ings[ing] = {'amount': 0, 'unit': ''}
                    ings[ing]['amount'] = amount
                    ings[ing]['unit'] = unit
                else:
                    ings[ing]['amount'] += amount
        content = ''
        for name, props in ings.items():
            content += (
                f"{name} ~~~ {props['amount']} "
                f"({props['unit']})\n"
            )
        response = HttpResponse(content, content_type="text/plain")
        return response


class RedirectShortLinkView(APIView):
    def get(self, request, linkID):
        shorturl = get_object_or_404(ShortUrl, short_link=linkID)
        return redirect(f'/recipes/{shorturl.shortlink.id}')
