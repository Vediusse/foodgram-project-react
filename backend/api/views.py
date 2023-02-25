import io

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Recipe, Tag, Ingredient, Favorite, Cart, RecipeIngredient
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
    AddSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    @staticmethod
    def add_object(model, user: settings.AUTH_USER_MODEL, pk: int):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "Рецепт уже добавлен в список"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = AddSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(model, user: settings.AUTH_USER_MODEL, pk: int) -> Response:
        object = model.objects.filter(user=user, recipe__id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Рецепт уже удален"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        url_path="favorite",
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.add_object(model=Favorite, user=request.user, pk=pk)
        elif request.method == "DELETE":
            return self.delete_object(model=Favorite, user=request.user, pk=pk)
        return None

    @action(
        detail=True,
        url_path="shopping_cart",
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return self.add_object(model=Cart, user=request.user, pk=pk)
        elif request.method == "DELETE":
            return self.delete_object(model=Cart, user=request.user, pk=pk)
        return None

    @action(
        detail=False,
        url_path="download_shopping_cart",
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        carts = Cart.objects.filter(user=request.user)
        ingredients = {}
        for cart in carts:
            recipe_obj = cart.recipe
            recipe_ingredient_objects_list = RecipeIngredient.objects.filter(
                recipe=recipe_obj
            )
            for recipe_ingredient_obj in recipe_ingredient_objects_list:
                ingredient_obj = recipe_ingredient_obj.ingredient
                amount = recipe_ingredient_obj.amount
                if ingredient_obj.name in ingredients.keys():
                    ingredients[ingredient_obj.name][0] += amount
                else:
                    ingredients[ingredient_obj.name] = [
                        amount,
                        ingredient_obj.measurement_unit,
                    ]

        file = io.BytesIO()
        for key, value in ingredients.items():
            amount, measurement_unit = value
            file.write(str.encode(f"{key} ({measurement_unit}) — {amount}\n"))
        file.seek(0)
        return FileResponse(file, filename="список покупок.txt")

    @action(
        detail=True,
        url_path="favorite",
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):

        if request.method == "POST":
            print(pk)
            return self.add_object(Favorite, request.user, pk=pk)
        elif request.method == "DELETE":
            return self.delete_object(Favorite, request.user, pk=pk)
        return None

    @action(
        detail=True,
        url_path="shopping_cart",
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return self.add_object(Cart, request.user, pk)
        elif request.method == "DELETE":
            return self.delete_object(Cart, request.user, pk)
        return None


class TagsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
