# Generated by Django 5.2 on 2025-04-05 18:39

from django.db import migrations, models

import core.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=core.utils.genereate_id,
                        editable=False,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone", models.CharField(blank=True, max_length=12, null=True)),
                ("company", models.CharField(blank=True, max_length=100, null=True)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("inactive", "Inactive"),
                            ("prospect", "Prospect"),
                        ],
                        default="active",
                        max_length=10,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
                "ordering": ["-updated_at"],
            },
        ),
    ]
