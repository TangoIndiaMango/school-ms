# Generated by Django 5.0.1 on 2024-02-07 13:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_artifacts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semesters', to='school_artifacts.session'),
        ),
    ]
