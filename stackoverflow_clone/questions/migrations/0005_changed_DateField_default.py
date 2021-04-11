import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_auto_20210410_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='dated',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
