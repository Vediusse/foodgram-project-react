from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from users.serializers import CustomUserSerializer
from .models import Recipe, Tag, RecipeIngredient, Ingredient, TagIngredient

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
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

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
        )

    @staticmethod
    def add_records_to_linked_models(recipe_obj, recipeingredient_set, tags):
        for recipeingredient in recipeingredient_set:
            ingredient_obg = recipeingredient.get("ingredient").get("id")
            amount = recipeingredient.get("amount")
            RecipeIngredient.objects.create(
                recipe=recipe_obj,
                ingredient=ingredient_obg,
                amount=amount,
            )
        for tag_obg in tags:
            TagIngredient.objects.create(
                recipe=recipe_obj,
                tag=tag_obg,
            )

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user
        recipeingredient_set = validated_data.pop("recipeingredient_set")
        tags = validated_data.pop("tags")
        recipe_obj = Recipe.objects.create(**validated_data)
        self.add_records_to_linked_models(
            recipe_obj=recipe_obj, recipeingredient_set=recipeingredient_set, tags=tags
        )

        return recipe_obj

    def update(self, instance, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user
        recipeingredient_set = validated_data.pop("recipeingredient_set")
        tags = validated_data.pop("tags")
        recipe_obj = instance
        RecipeIngredient.objects.filter(
            recipe=recipe_obj,
        ).delete()
        TagIngredient.objects.filter(
            recipe=recipe_obj,
        ).delete()
        self.add_records_to_linked_models(
            recipe_obj=recipe_obj, recipeingredient_set=recipeingredient_set, tags=tags
        )

        return recipe_obj
