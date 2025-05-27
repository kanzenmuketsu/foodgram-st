from django.urls import include, path
from rest_framework.routers import DefaultRouter
from profiles.views import CustomUserViewSet
from posts.views import IngredientViewSet


router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('ingredients', IngredientViewSet, basename="Ingredient")


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
