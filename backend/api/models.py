from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from colorfield.fields import ColorField


class Ingredient(models.Model):
    name = models.CharField(unique=True, max_length=100)
    measurement_unit = models.CharField(max_length=20)


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
        related_name="recipe",
        verbose_name="Автор",
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    tags = models.ManyToManyField(
        to=Tag,
        through="TagIngredient",
        related_name="ingredients",
        verbose_name="ингредиент",
    )
    image = models.ImageField(upload_to="recipes/images/")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through="RecipeIngredient",
        related_name="ingredients",
        verbose_name="ингредиент",
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления", validators=(MinValueValidator(1, "Min 1."),)
    )


class TagIngredient(models.Model):
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
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"], name="unique ingredients recipe"
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe")

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique recipe",
            )
        ]


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipes")

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique recipes",
            )
        ]
