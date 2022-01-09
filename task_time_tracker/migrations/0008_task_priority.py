# Generated by Django 3.2.9 on 2022-01-08 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_time_tracker', '0007_alter_task_actual_mins'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.IntegerField(blank=True, choices=[(None, 'None'), (3, 'High'), (2, 'Medium'), (1, 'Low')], null=True),
        ),
    ]