from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=255)


class Question(models.Model):
    title = models.TextField()
    text = models.TextField()
    pub_date = models.DateTimeField("date publicated", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    #tags = models.ManyToManyField('Tag')


class Answer(models.Model):
    title = models.TextField()
    text = models.TextField()
    pub_date = models.DateTimeField("date publicated", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
