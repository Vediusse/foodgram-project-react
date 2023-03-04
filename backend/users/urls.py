from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import SubscribesViewSet

app_name = "user"
router = SimpleRouter()

router.register("", SubscribesViewSet, basename="subscriptions")

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("users/", include(router.urls)),
]
