# Generated by Django 5.0.1 on 2024-02-08 10:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_administration', '0006_remove_department_faculty_department_courses_and_more'),
        ('users', '0003_alter_customuser_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecturer',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lecturer_level', to='school_administration.level'),
        ),
        migrations.AddField(
            model_name='student',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_level', to='school_administration.level'),
        ),
        migrations.AddField(
            model_name='student',
            name='student_dept',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_dept', to='school_administration.department'),
        ),
    ]