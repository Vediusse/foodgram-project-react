from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet
from .models import Subscribers, User
from .serializers import CustomUserSerializer, SubscribeSerializer
from django.conf import settings


class SubscribesViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {"errors": "Вы не можете подписываться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Subscribers.objects.filter(user=user, subscribed=author).exists():
            return Response(
                {"errors": "Вы уже подписаны на данного пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscribe = Subscribers.objects.create(user=user, subscribed=author)
        serializer = SubscribeSerializer(subscribe, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribers.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
