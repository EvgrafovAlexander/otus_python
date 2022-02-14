from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=255)


class Post(models.Model):
    header = models.TextField()
    text = models.TextField()
    created_date = models.DateTimeField("date created", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    tags = models.ManyToManyField('Tag')
