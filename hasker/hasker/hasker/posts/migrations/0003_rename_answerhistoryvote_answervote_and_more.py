# Generated by Django 4.1.2 on 2022-10-29 12:14

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0002_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AnswerHistoryVote",
            new_name="AnswerVote",
        ),
        migrations.RenameModel(
            old_name="QuestionHistoryVote",
            new_name="QuestionVote",
        ),
    ]