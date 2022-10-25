from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField("email address", max_length=254, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to="thumbpath", blank=True, null=True)
    reg_date = models.DateField("registered date", auto_now_add=True)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.username
