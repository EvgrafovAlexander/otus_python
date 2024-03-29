# Generated by Django 4.1.2 on 2022-10-29 15:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0003_rename_answerhistoryvote_answervote_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="answervote",
            name="is_plus",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="questionvote",
            name="is_plus",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="answer",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="authors", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="answer",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="posts.question"
            ),
        ),
    ]
