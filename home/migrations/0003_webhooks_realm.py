# Generated by Django 3.2.5 on 2021-09-04 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20210904_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhooks',
            name='realm',
            field=models.IntegerField(default=0),
        ),
    ]
