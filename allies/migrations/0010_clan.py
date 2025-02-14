# Generated by Django 3.2.5 on 2021-09-26 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("allies", "0009_auto_20201217_1950"),
    ]

    operations = [
        migrations.CreateModel(
            name="Clan",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        db_index=True, primary_key=True, serialize=False
                    ),
                ),
                ("game_id", models.IntegerField(null=True)),
                ("owner_id", models.IntegerField(null=True)),
                ("group_avatar_id", models.IntegerField(null=True)),
                ("name", models.CharField(max_length=255, null=True)),
                ("tag", models.CharField(max_length=255, null=True)),
                ("description", models.CharField(max_length=255, null=True)),
                ("permanent", models.CharField(max_length=255, null=True)),
                ("exclusive", models.CharField(max_length=255, null=True)),
                ("member_limit", models.CharField(max_length=255, null=True)),
                ("expire_date", models.CharField(max_length=255, null=True)),
                ("create_date", models.CharField(max_length=255, null=True)),
                ("delete_date", models.CharField(max_length=255, null=True)),
                ("region", models.IntegerField(null=True)),
                ("language", models.CharField(max_length=255, null=True)),
                ("active", models.CharField(max_length=255, null=True)),
                ("join_policy", models.IntegerField(null=True)),
                ("required_stats", models.IntegerField(null=True)),
                ("allow_join", models.CharField(max_length=255, null=True)),
                ("auto_accept_join", models.CharField(max_length=255, null=True)),
                ("permanent_limit", models.IntegerField(null=True)),
                ("role_limit", models.CharField(max_length=255, null=True)),
                ("max_role_limit", models.CharField(max_length=255, null=True)),
                ("member_count", models.IntegerField(null=True)),
            ],
        ),
    ]
