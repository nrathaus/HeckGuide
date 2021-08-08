# Generated by Django 3.2.5 on 2021-08-07 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorldSegments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255, null=True)),
                ('game_id', models.IntegerField(null=True)),
                ('inbound_marches', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('object_id', models.BigIntegerField(null=True)),
                ('outbound_marches', models.BigIntegerField(null=True)),
                ('owner_group_id', models.BigIntegerField(null=True)),
                ('owner_group_name', models.CharField(max_length=255, null=True)),
                ('owner_user_id', models.BigIntegerField(null=True)),
                ('owner_username', models.CharField(max_length=255, null=True)),
                ('state', models.IntegerField(null=True)),
                ('state_expiry_time', models.BigIntegerField(null=True)),
                ('timestamp', models.BigIntegerField(null=True)),
                ('world_id', models.IntegerField(null=True)),
                ('x', models.IntegerField(null=True)),
                ('y', models.IntegerField(null=True)),
                ('z', models.IntegerField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
