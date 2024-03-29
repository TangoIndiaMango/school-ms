# Generated by Django 5.0.1 on 2024-02-13 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_remove_course_departments'),
        ('school_administration', '0015_remove_department_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='courses',
            field=models.ManyToManyField(blank=True, related_name='department', to='courses.course'),
        ),
    ]
