# Generated by Django 4.2.9 on 2024-07-04 12:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reaktion", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="runevent",
            name="handle",
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name="workspace",
            name="pinned_by",
            field=models.ManyToManyField(
                blank=True,
                help_text="The users that have pinned the workspace",
                related_name="pinned_workspaces",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]