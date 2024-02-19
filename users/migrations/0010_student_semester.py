# Generated by Django 5.0.1 on 2024-02-19 04:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_artifacts', '0005_alter_session_semesters'),
        ('users', '0009_rename_lecturer_dept_lecturer_lecturer_department_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student', to='school_artifacts.semester'),
        ),
    ]