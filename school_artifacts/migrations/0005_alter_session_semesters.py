# Generated by Django 5.0.1 on 2024-02-19 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_artifacts', '0004_alter_session_semesters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='semesters',
            field=models.ManyToManyField(blank=True, related_name='session', to='school_artifacts.semester'),
        ),
    ]
