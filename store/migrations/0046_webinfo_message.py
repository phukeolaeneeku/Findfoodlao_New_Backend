# Generated by Django 4.2.4 on 2024-10-31 03:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0045_categorymodel_sorted_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="webinfo",
            name="message",
            field=models.TextField(blank=True, null=True),
        ),
    ]