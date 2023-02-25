from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import User, Subscribers
from api.models import Recipe


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, user):
        request = self.context["request"]
        author = request.user
        return any(
            user == subscribeds_user.subscribed
            for subscribeds_user in author.subscribed_users
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
        )


class SubscribeSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="subscribed.username")
    email = serializers.ReadOnlyField(source="subscribed.email")
    first_name = serializers.ReadOnlyField(source="subscribed.first_name")
    last_name = serializers.ReadOnlyField(source="subscribed.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = Subscribers
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
        )

    def get_is_subscribed(self, subscribes):
        request = self.context["request"]
        author = request.user
        return any(
            subscribes.subscribed == subscribeds_user.subscribed
            for subscribeds_user in author.subscribed_users
        )

    def get_recipes(self, subscribers):
        recipes = Recipe.objects.filter(author=subscribers.subscribed)
        recipes_list = []
        for recipe in recipes:
            recipes_list.append(
                {
                    "id": recipe.id,
                    "name": recipe.name,
                    "image": recipe.image,
                    "cooking_time": recipe.cooking_time,
                }
            )
