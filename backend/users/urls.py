from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscribesViewSet

app_name = "api"

router = DefaultRouter()
router.register("users", SubscribesViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
