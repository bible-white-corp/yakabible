# Generated by Django 2.2 on 2019-06-03 22:07

import billapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0004_auto_20190514_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='promotion_image_path',
            field=models.ImageField(blank=True, null=True, upload_to=billapp.models.promo_image_path),
        ),
    ]
