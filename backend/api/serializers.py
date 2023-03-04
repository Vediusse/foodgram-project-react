from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from users.serializers import CustomUserSerializer

from .models import (
    Recipe,
    Tag,
    RecipeIngredient,
    Ingredient,
    Cart,
    TagRecipe,
    Favorite,
)

user = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient.id", queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class AddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        read_only_fields = fields


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source="recipeingredient_set",
        many=True,
    )
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(validators=(MinValueValidator(1),))

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        amounts = [ingredient["amount"] for ingredient in ingredients]
        ingredients_id = [ingredient["id"] for ingredient in ingredients]
        errors = {}
        if not ingredients:
            errors["ingredients_error"] = "Нужен хоть один ингридиент для рецепта"

        if len(ingredients) != len(set(ingredients_id)):
            errors["ingredients_id_error"] = "У вас два одинаковвых ингредиента"

        if any((int(amount) <= 0 for amount in amounts)):
            errors[
                "amount_error"
            ] = "Убедитесь, что значение количества ингредиента больше 0"

        if errors:
            raise serializers.ValidationError(errors)
        return data

    def get_is_favorited(self, recipe):
        request = self.context["request"]
        author = request.user
        if isinstance(author, AnonymousUser):
            return False
        return Favorite.objects.filter(user=author, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context["request"]
        author = request.user
        if isinstance(author, AnonymousUser):
            return False
        return Cart.objects.filter(user=author, recipe=recipe).exists()

    @staticmethod
    def add_records_to_linked_models(recipe_obj, ingredients, tags):
        for tag in tags:
            TagRecipe.objects.create(recipe=recipe_obj, tag=Tag.objects.get(id=tag))
        for ingredient in ingredients:
            ingredient_obg = ingredient.get("ingredient").get("id")
            amount = ingredient.get("amount")
            RecipeIngredient.objects.create(
                recipe=recipe_obj,
                ingredient=ingredient_obg,
                amount=amount,
            )

    def create(self, validated_data):
        request = self.context["request"]
        ingredients = validated_data.pop("recipeingredient_set")
        tags = request.data["tags"]
        recipe_obj = Recipe.objects.create(author=request.user, **validated_data)
        self.add_records_to_linked_models(
            recipe_obj=recipe_obj, ingredients=ingredients, tags=tags
        )

        return recipe_obj

    def update(self, instance, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user
        ingredients = validated_data.pop("recipeingredient_set")
        tags = request.data["tags"]
        recipe_obj = instance
        RecipeIngredient.objects.filter(
            recipe=recipe_obj,
        ).delete()
        TagRecipe.objects.filter(
            recipe=recipe_obj,
        ).delete()
        self.add_records_to_linked_models(
            recipe_obj=recipe_obj, ingredients=ingredients, tags=tags
        )

        return recipe_obj
