# Generated by Django 5.0.1 on 2024-02-06 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=20, unique=True)),
                ('course_name', models.CharField(max_length=100)),
                ('course_description', models.TextField()),
                ('course_credit', models.IntegerField()),
                ('course_unit', models.IntegerField()),
                ('course_level', models.CharField(max_length=20)),
                ('course_semester', models.CharField(max_length=70)),
                ('course_status', models.BooleanField(default=True)),
                ('mark', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='CourseRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('register_now', models.BooleanField(default=False)),
                ('allow_debtor', models.BooleanField(default=False)),
                ('processing_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('late_reg_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
