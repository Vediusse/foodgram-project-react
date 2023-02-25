from django.contrib import admin

from .models import Ingredient, Recipe, Tag, TagIngredient, RecipeIngredient

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(TagIngredient)
admin.site.register(RecipeIngredient)
