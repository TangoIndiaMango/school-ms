# Generated by Django 5.0.1 on 2024-02-17 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_artifacts', '0003_remove_semester_session_session_semesters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='semesters',
            field=models.ManyToManyField(blank=True, related_name='sessions', to='school_artifacts.semester'),
        ),
    ]
