# Generated by Django 3.2.5 on 2024-11-24 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_task_task_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.CharField(choices=[('GENERIC', 'Generic'), ('DB_IMPORT', 'Database Import'), ('DB_UPDATE', 'Database Update'), ('DB_EXPORT', 'Database Export')], default='GENERIC', help_text='Type of the task', max_length=30),
        ),
    ]
