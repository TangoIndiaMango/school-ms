# Generated by Django 5.0.1 on 2024-02-13 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_remove_course_departments'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='departments',
            field=models.ManyToManyField(blank=True, related_name='courses', to='courses.course'),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_credit',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_unit',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
