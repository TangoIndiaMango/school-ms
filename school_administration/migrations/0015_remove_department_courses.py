# Generated by Django 5.0.1 on 2024-02-13 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school_administration', '0014_department_program_duration_alter_faculty_dean'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='courses',
        ),
    ]