# Generated by Django 5.0.1 on 2024-02-06 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school_administration', '0003_remove_department_courses_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='level',
            name='level_department',
        ),
    ]