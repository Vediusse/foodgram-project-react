from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls"), name="user"),
    path("api/", include("api.urls"), name="api"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
