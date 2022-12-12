# Generated by Django 4.1.4 on 2022-12-12 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("task_time_tracker", "0003_auto_20220212_1824"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="priority",
            field=models.IntegerField(
                blank=True,
                choices=[(None, "—-"), (3, "High"), (2, "Medium"), (1, "Low")],
                null=True,
            ),
        ),
    ]
