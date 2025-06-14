from rest_framework.response import Response
from rest_framework import status
from djoser.views import UserViewSet
from rest_framework.decorators import action
from .models import Profile
from posts.serializers import RecipiShortSerializer
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated


class CustomUserViewSet(UserViewSet):
    @action(detail=True, methods=['put', 'delete'])
    def avatar(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if request.method == "DELETE":
            user.avatar = None
            user.save()
            return Response({'status': 'avatar deleted'})
        serializer.is_valid(raise_exception=True)
        avatar = serializer.validated_data.get('avatar', False)
        if avatar:
            user.avatar = avatar
            user.save()
            return Response({'status': 'avatar set'})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        user = self.request.user
        try:
            target = Profile.objects.get(pk=kwargs['id'])
        except Exception:
            return Response(
                {"subscribe": "Профиль не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        #  Почему внутри view-функции не разрешено выполнять проверку?
        #  Проверка до вызова serializer = нет лишней работы,
        #  К тому же, запрос пустой. Что там сериализировать?
        if user == target:
            return Response(
                {"subscribe": "Нельзя подписаться на себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        already_follow = target.followers.filter(pk=user.id).exists()

        if request.method == "DELETE":
            if not already_follow:
                return Response(
                    {"subscribe": "Вы не были подписаны"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target.followers.remove(user)
            return Response(
                {},
                status=status.HTTP_204_NO_CONTENT
            )
        if already_follow:
            return Response(
                {"subscribe": "Вы уже подписаны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        limit = request.query_params.get('recipes_limit', None)
        if limit:
            limit = int(limit)

        target.followers.add(user)
        serializer = self.get_serializer(
            target, data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.data

        validated_data = self.add_recipes_field(
            validated_data, target, limit
        )

        return Response(
            validated_data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user

        paginator = LimitOffsetPagination()
        recipes_limit = request.query_params.get('recipes_limit', None)
        if recipes_limit:
            recipes_limit = int(recipes_limit)

        flws = user.flws.all()

        serializer = self.get_serializer(flws, many=True)
        validated_data = serializer.data
        for i in validated_data:
            target = get_object_or_404(Profile, pk=i['id'])
            i = self.add_recipes_field(i, target, recipes_limit)

        validated_data = paginator.paginate_queryset(validated_data, request)
        return paginator.get_paginated_response(validated_data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        paginator = LimitOffsetPagination()
        bookmared = request.user.bookmared.all()
        serializer = RecipiShortSerializer(bookmared, many=True)
        bookmared = paginator.paginate_queryset(serializer.data, request)
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def cart(self, request, *args, **kwargs):
        paginator = LimitOffsetPagination()
        cart = request.user.cart.all()

        serializer = RecipiShortSerializer(cart, many=True)

        cart = paginator.paginate_queryset(serializer.data, request)
        return paginator.get_paginated_response(serializer.data)

    def add_recipes_field(self, validated_data, target, limit):
        recipes_count = target.recipi_author.count()
        validated_data['recipes_count'] = recipes_count

        recipes = target.recipi_author.all().order_by('-id')
        serializer = RecipiShortSerializer(
            recipes,
            many=True,
            context=self.get_serializer_context()
        )
        validated_data['recipes'] = serializer.data[:limit]

        return validated_data
