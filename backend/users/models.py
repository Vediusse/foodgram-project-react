from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        "Email",
        max_length=200,
        unique=True,
    )
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)

    @property
    def subscribed_users(self):
        return Subscribers.objects.filter(user=self)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.email


class Subscribers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    subscribed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribed"
    )

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscribed"],
                name="unique follow",
            )
        ]
