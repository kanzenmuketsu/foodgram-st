from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import Ingredient, Recipi
from .serializers import IngredientSerializer, RecipiSerializer


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
