# Generated by Django 4.1.2 on 2022-10-29 11:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("posts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="questionhistoryvote",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="qh_user", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="questions", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="tags",
            field=models.ManyToManyField(related_name="tag", to="posts.tag"),
        ),
        migrations.AddField(
            model_name="answerhistoryvote",
            name="answer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="aq_answer", to="posts.answer"
            ),
        ),
        migrations.AddField(
            model_name="answerhistoryvote",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="aq_user", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="answer",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="answers", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="answer",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="posts.question"
            ),
        ),
    ]
