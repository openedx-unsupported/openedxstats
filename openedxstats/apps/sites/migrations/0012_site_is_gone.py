# Generated by Django 1.9.5 on 2018-02-28 10:50
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0011_auto_20180205_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='is_gone',
            field=models.BooleanField(default=False),
        ),
    ]
