import io

from django.conf import settings
from django.db.models import Count
from django.db.models import F
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from users.permissions import IsAuthorOrReadOnly

from .filters import IngredientSearchFilter
from .models import Recipe, Tag, Ingredient, Favorite, Cart, RecipeIngredient
from .paginator import CustomPaginator
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
    AddSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    http_method_names = ("get", "post", "patch", "delete")
    pagination_class = CustomPaginator
    filter_backends = (filters.OrderingFilter,)
    ordering = ("-id",)

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = (AllowAny,)

        if self.request.method == "POST":
            self.permission_classes = (IsAuthenticated,)

        if self.request.method in ("PATCH", "DELETE"):
            self.permission_classes = (IsAuthorOrReadOnly,)

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if self.request.user.is_anonymous:
            is_favorited, is_in_shopping_cart = False, False
        else:
            is_favorited = self.request.query_params.get("is_favorited")
            is_in_shopping_cart = self.request.query_params.get("is_in_shopping_cart")
        tags = self.request.query_params.getlist("tags")
        author = self.request.query_params.get("author")
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if is_favorited:
            queryset = queryset.filter(users_favorites=self.request.user).distinct()

        if is_in_shopping_cart:
            queryset = queryset.filter(users_shopping_cart=self.request.user).distinct()
        if author:
            queryset = queryset.filter(author__id=author).all()
        return queryset

    @staticmethod
    def add_object(model, user: settings.AUTH_USER_MODEL, pk: int):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "Ошибка добавления"},
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
        return Response({"errors": "Ошибка "}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        carts = Cart.objects.filter(user=request.user).values_list("recipe")
        ingredients = (
            RecipeIngredient.objects.filter(recipe__in=carts)
            .values("ingredient__name")
            .annotate(measurement_unit=F("ingredient__measurement_unit"))
            .annotate(amount=F("amount"))
            .annotate(count=Count("ingredient"))
        )
        file = io.BytesIO()
        for ingredient in ingredients:
            info = list(ingredient.values())
            file.write(
                str.encode("{} ({}) - {}\n".format(info[0], info[1], info[2] * info[3]))
            )
        file.seek(0)
        return FileResponse(file, filename="shopping cart.txt")


class TagsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)
    queryset = Ingredient.objects.all()
