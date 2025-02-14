# Generated by Django 3.2.5 on 2021-10-04 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("poll", "0003_realmlist"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClanChat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mail_id", models.IntegerField(null=True)),
                ("username", models.CharField(max_length=255, null=True)),
                ("message", models.CharField(max_length=255, null=True)),
                ("timestamp", models.IntegerField(null=True)),
                ("user_id", models.IntegerField(null=True)),
                ("user_avatar_id", models.IntegerField(null=True)),
                ("user_avatar_type", models.IntegerField(null=True)),
                ("message_type", models.IntegerField(null=True)),
                ("item_id", models.IntegerField(null=True)),
                ("realm", models.IntegerField(null=True)),
            ],
        ),
    ]
