import base64
import os

from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=20)

    class Meta:
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique name ingredient",
            )
        ]


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    color = ColorField(default="#FF0000", unique=True)
    slug = models.SlugField(
        max_length=50,
        verbose_name="Слаг тега",
        validators=(
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Недопустимые символы в слаге",
            ),
        ),
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipe_author",
        verbose_name="Автор",
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    tags = models.ManyToManyField(
        to=Tag,
        through="TagRecipe",
        related_name="recipe_tags",
        verbose_name="теги",
    )
    image = models.ImageField(upload_to="media/recipes/images/")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through="RecipeIngredient",
        related_name="recipe_ingredients",
        verbose_name="ингредиент",
    )
    users_favorites = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        through="Favorite",
        related_name="recipe_favorite",
        verbose_name="избранные",
    )
    users_shopping_cart = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        through="Cart",
        related_name="recipe_cart",
        verbose_name="избранные",
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления", validators=(MinValueValidator(1, "Min 1."),)
    )

    @staticmethod
    def image_as_base64(image_file, format="png"):
        """
        :param `image_file` for the complete path of image.
        :param `format` is format for image, eg: `png` or `jpg`.
        """
        if not os.path.isfile(image_file):
            return None

        encoded_string = ""
        with open(image_file, "rb") as img_f:
            encoded_string = base64.b64encode(img_f.read())
        return "data:image/%s;base64,%s" % (format, encoded_string)

    @property
    def get_image_base64(self):
        return self.image_as_base64(settings.MEDIA_ROOT + self.image.path)


class Favorite(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        to=Recipe, on_delete=models.CASCADE, related_name="favorite"
    )

    class Meta:
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique favorite recipe",
            )
        ]


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        to=Tag,
        on_delete=models.CASCADE,
        verbose_name="тег",
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name="рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "tag"),
                name="уникальный тег для рецепта",
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name="рецепт",
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        verbose_name="ингредиент",
    )
    amount = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="уникальный ингредиент для рецепта",
            )
        ]


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="cart")

    class Meta:
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique cart user",
            )
        ]
