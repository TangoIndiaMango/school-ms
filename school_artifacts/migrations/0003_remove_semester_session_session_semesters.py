# Generated by Django 5.0.1 on 2024-02-08 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_artifacts', '0002_alter_semester_session'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semester',
            name='session',
        ),
        migrations.AddField(
            model_name='session',
            name='semesters',
            field=models.ManyToManyField(related_name='sessions', to='school_artifacts.semester'),
        ),
    ]