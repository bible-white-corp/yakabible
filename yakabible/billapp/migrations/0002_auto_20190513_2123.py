# Generated by Django 2.2 on 2019-05-13 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='validation_state',
            field=models.SmallIntegerField(choices=[(1, 'Need authorization'), (2, 'Approved by the association'), (3, 'Approved by EPITA'), (4, 'Authorized')], default=1),
        ),
    ]
