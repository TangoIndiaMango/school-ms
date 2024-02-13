# Generated by Django 5.0.1 on 2024-02-08 10:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_alter_course_course_level'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseregistration',
            old_name='session',
            new_name='semester',
        ),
        migrations.RemoveField(
            model_name='course',
            name='course_level',
        ),
        migrations.RemoveField(
            model_name='course',
            name='course_semester',
        ),
        migrations.RemoveField(
            model_name='courseregistration',
            name='allow_debtor',
        ),
        migrations.RemoveField(
            model_name='courseregistration',
            name='late_reg_fee',
        ),
        migrations.RemoveField(
            model_name='courseregistration',
            name='processing_fee',
        ),
        migrations.RemoveField(
            model_name='courseregistration',
            name='register_now',
        ),
        migrations.CreateModel(
            name='CourseRegSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('register_now', models.BooleanField(default=False)),
                ('allow_debtor', models.BooleanField(default=False)),
                ('processing_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('late_reg_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course_reg_settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.courseregistration')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]