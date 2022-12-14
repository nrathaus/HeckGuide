from django.db import models


class WorldSegments(models.Model):
    # activities = models.CharField(max_length=255,null=True)
    # components = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    game_id = models.IntegerField(null=True)
    inbound_marches = models.IntegerField(null=True)
    # level = models.IntegerField(null=True)
    name = models.CharField(max_length=255, null=True)
    object_id = models.BigIntegerField(null=True, db_index=True)
    # object_type = models.IntegerField(null=True)
    outbound_marches = models.BigIntegerField(null=True)
    owner_group_id = models.BigIntegerField(null=True)
    owner_group_name = models.CharField(max_length=255, null=True)
    owner_user_id = models.BigIntegerField(null=True)
    owner_username = models.CharField(max_length=255, null=True)
    # row_version = models.IntegerField(null=True)
    # size = models.IntegerField(null=True)
    state = models.IntegerField(null=True)
    state_expiry_time = models.BigIntegerField(null=True)
    timestamp = models.BigIntegerField(null=True)
    world_id = models.IntegerField(null=True)
    x = models.IntegerField(null=True)
    y = models.IntegerField(null=True)
    z = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False
    )
