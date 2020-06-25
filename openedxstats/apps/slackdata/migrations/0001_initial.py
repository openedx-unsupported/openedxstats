# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 19:01
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MessageCountByDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SlackUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('deleted', models.BooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='messagecountbyday',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slackdata.SlackUser'),
        ),
        migrations.AlterUniqueTogether(
            name='messagecountbyday',
            unique_together=set([('user', 'date')]),
        ),
        migrations.AlterIndexTogether(
            name='messagecountbyday',
            index_together=set([('user', 'date')]),
        ),
    ]
