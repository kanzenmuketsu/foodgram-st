from django.urls import include, path
from rest_framework.routers import DefaultRouter
from profiles.views import CustomUserViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
