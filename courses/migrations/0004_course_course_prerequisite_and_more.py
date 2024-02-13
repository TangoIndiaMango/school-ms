# Generated by Django 5.0.1 on 2024-02-06 11:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_initial'),
        ('school_administration', '0003_remove_department_courses_and_more'),
        ('school_artifacts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_prerequisite',
            field=models.ManyToManyField(to='courses.course'),
        ),
        migrations.RemoveField(
            model_name='course',
            name='course_level',
        ),
        migrations.AlterField(
            model_name='course',
            name='course_semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_semesters', to='school_artifacts.semester'),
        ),
        migrations.AddField(
            model_name='course',
            name='course_level',
            field=models.ManyToManyField(related_name='course_levels', to='school_administration.level'),
        ),
    ]