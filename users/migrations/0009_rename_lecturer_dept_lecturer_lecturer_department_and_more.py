# Generated by Django 5.0.1 on 2024-02-10 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_lecturer_lecturer_dept'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lecturer',
            old_name='lecturer_dept',
            new_name='lecturer_department',
        ),
        migrations.RenameField(
            model_name='student',
            old_name='student_dept',
            new_name='student_department',
        ),
    ]
