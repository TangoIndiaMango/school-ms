# Generated by Django 5.0.1 on 2024-02-10 16:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_administration', '0013_department_courses'),
        ('users', '0006_alter_lecturer_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='program_duration',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='faculty',
            name='dean',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dean', to='users.lecturer'),
        ),
    ]
