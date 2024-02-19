# Generated by Django 5.0.1 on 2024-02-14 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_alter_course_course_code_alter_course_course_credit_and_more'),
        ('school_artifacts', '0003_remove_semester_session_session_semesters'),
        ('users', '0009_rename_lecturer_dept_lecturer_lecturer_department_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='courseregistration',
            unique_together={('student', 'course', 'semester')},
        ),
        migrations.RemoveField(
            model_name='courseregistration',
            name='level',
        ),
    ]