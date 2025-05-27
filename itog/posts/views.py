from rest_framework.viewsets import ModelViewSet
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


import json
with open('../data/ingredients.json', encoding='utf-8') as f:
    data = json.load(f)
    for i in data:
        print(i)

        so = Ingredient(**i)
        print(so)
        #so.save()