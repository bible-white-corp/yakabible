# Generated by Django 2.2 on 2019-06-03 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0004_auto_20190514_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='association',
            name='url',
            field=models.TextField(default=None, max_length=64),
        ),
    ]