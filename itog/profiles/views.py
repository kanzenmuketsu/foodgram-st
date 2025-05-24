from rest_framework.response import Response
from rest_framework import status
from djoser.views import UserViewSet
from rest_framework.decorators import action


class CustomUserViewSet(UserViewSet):

    @action(detail=True, methods=['put', 'delete'])
    def avatar(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if request.method == "DELETE":
            user.avatar = None
            user.save()
            return Response({'status': 'avatar deleted'})

        if serializer.is_valid():
            user.avatar = serializer.validated_data['avatar']
            user.save()
            return Response({'status': 'avatar set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
