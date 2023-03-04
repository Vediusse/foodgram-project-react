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
            "first_name",
            "last_name",
            "password",
        )


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="subscribed.username")
    id = serializers.ReadOnlyField(source="subscribed.id")
    email = serializers.ReadOnlyField(source="subscribed.email")
    first_name = serializers.ReadOnlyField(source="subscribed.first_name")
    last_name = serializers.ReadOnlyField(source="subscribed.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
            "recipes_count",
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
        return SubscribeRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.subscribed).count()
