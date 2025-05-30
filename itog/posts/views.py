from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from .models import Ingredient, Recipi, ShortUrl
from .serializers import (
    IngredientSerializer, RecipiSerializer,
    RecipiShortLinkSerializer
)

from django.shortcuts import get_object_or_404, redirect
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
import uuid


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer

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
        cart = self.request.query_params.get('cart', False)
        if pk:
            qset = qset.filter(author=pk)
        if bookmared:
            qset = qset.filter(bookmared__exact=self.request.user.id)
        if cart:
            qset = qset.filter(cart__exact=self.request.user.id)
        return qset

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
                print(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            else:
                short_link = uuid.uuid4().hex[:4]
                obj.short_link = ShortUrl.objects.create(short_link=short_link)
                obj.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )


class RedirectShortLinkView(APIView):
    def get(self, request, linkID):
        shorturl = get_object_or_404(ShortUrl, short_link=linkID)
        return redirect(f'/api/recipes/{shorturl.shortlink.id}')
