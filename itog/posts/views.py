from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from .models import Ingredient, Recipi, ShortUrl
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

    def get_queryset(self):
        qset = Recipi.objects.all()
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

    def destroy(self, request, *args, **kwargs):
        if not request.user == self.get_object().author:
            return Response(
                {"recipi": "Вы не автор"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = RecipiShortLinkSerializer(
            obj, data=request.data, partial=True
        )

        if serializer.is_valid():
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
        if request.method == 'POST':
            if obj in list(bookmared.all()):
                return Response(
                    {"recipi": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            bookmared.add(obj)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if obj not in list(bookmared.all()):
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
        if request.method == 'POST':
            if obj in list(cart.all()):
                return Response(
                    {"recipi": "Рецепт уже в корзине"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart.add(obj)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if obj not in list(cart.all()):
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
        ings = dict()
        for recipi in cart:
            for rrr in recipi.RRR.all():
                ing, amount = rrr.Ingredient.name, rrr.amount
                unit = rrr.Ingredient.measurement_unit
                if ing not in ings:
                    ings[ing] = {'amount': 0, 'unit': ''}
                    ings[ing]['amount'] = amount
                    ings[ing]['unit'] = unit
                else:
                    ings[ing]['amount'] += amount

        file_path = f'media/files/{request.user.username}_buylist.txt'
        with open(file_path, 'w', encoding='utf-8') as file:
            for name, props in ings.items():
                print(
                    f"--> {name} ~~~ {props['amount']} ({props['unit']})",
                    file=file
                )
        FilePointer = open(file_path, "r", encoding='utf-8')
        response = HttpResponse(
            FilePointer, content_type='text/plain'
        )
        response['Content-Disposition'] = 'attachment; filename=buylist.txt'

        return response


class RedirectShortLinkView(APIView):
    def get(self, request, linkID):
        shorturl = get_object_or_404(ShortUrl, short_link=linkID)
        return redirect(f'/recipes/{shorturl.shortlink.id}')
