from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tags', '0001_models_created'),
        ('users', '0001_models_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('body', models.TextField()),
                ('dated', models.DateField(auto_now_add=True)),
                ('likes', models.IntegerField(default=0)),
                ('tags', models.ManyToManyField(related_name='questions', to='tags.Tag')),
                ('user_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='users.UserAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.TextField()),
                ('dated', models.DateField(auto_now_add=True)),
                ('likes', models.IntegerField(default=0)),
                ('user_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='answers', to='users.UserAccount')),
            ],
        ),
    ]
