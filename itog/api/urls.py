from django.urls import include, path
from rest_framework.routers import DefaultRouter
from profiles.views import CustomUserViewSet
from posts.views import IngredientViewSet, RecipiViewSet

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('ingredients', IngredientViewSet, basename="Ingredient")
router.register('recipes', RecipiViewSet, basename='Recipi')


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
