# Generated by Django 2.2 on 2021-04-11 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0003_Added_question_fk_to_Answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
