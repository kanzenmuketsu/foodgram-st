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
        pk = self.request.query_params.get('author', False)
        if pk:
            return Recipi.objects.filter(author=pk)
        return Recipi.objects.all()
