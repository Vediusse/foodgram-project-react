from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import RecipeViewSet, TagsViewSet, IngredientsViewSet

app_name = "api"

router = SimpleRouter()

router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagsViewSet, basename="tags")
router.register("ingredients", IngredientsViewSet, basename="ingredients")


urlpatterns = [
    path("", include(router.urls)),
]
