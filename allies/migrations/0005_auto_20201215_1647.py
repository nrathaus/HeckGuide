# Generated by Django 3.1 on 2020-12-15 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("allies", "0004_auto_20201215_1505"),
    ]

    operations = [
        migrations.AlterField(
            model_name="currentally",
            name="cost",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="currentally",
            name="group_id",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="currentally",
            name="previous_cost",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="currentally",
            name="troop_kills",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalally",
            name="cost",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalally",
            name="group_id",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalally",
            name="previous_cost",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalally",
            name="troop_kills",
            field=models.BigIntegerField(null=True),
        ),
    ]
