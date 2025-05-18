from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
#  router.register()

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('v1/', include(router.urls))
]
