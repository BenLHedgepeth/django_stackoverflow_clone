# Generated by Django 2.2.4 on 2021-04-11 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_auto_20210411_0918'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'default_manager_name': 'objects', 'ordering': ['-dated']},
        ),
    ]
