from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.TextField()
    text = models.TextField()
    pub_date = models.DateTimeField("published date", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    votes = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    pub_date = models.DateTimeField("published date", auto_now_add=True)
    votes = models.IntegerField(default=0)
    is_right = models.BooleanField(default=False)

    def __str__(self):
        return self.text
