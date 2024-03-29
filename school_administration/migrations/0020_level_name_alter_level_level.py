# Generated by Django 5.0.1 on 2024-02-14 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_administration', '0019_level_courses'),
    ]
    
    def generate_default_level_names(apps, schema_editor):
        Level = apps.get_model('school_administration', 'Level')
        count = 1
        for level in Level.objects.all():
            level.name = f'Level {count}'
            level.save()
            count += 1
            

    operations = [
        migrations.AddField(
            model_name='level',
            name='name',
            field=models.CharField(max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.RunPython(generate_default_level_names),
        migrations.AlterField(
            model_name='level',
            name='level',
            field=models.IntegerField(),
        ),
    ]
