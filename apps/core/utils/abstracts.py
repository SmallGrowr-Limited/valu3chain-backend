import uuid

from django.db import models


class AbstractUUID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
        

class AbstractProfileSettings(AbstractUUID):
    address = models.CharField(blank=True, null=True, max_length=225)
    reg_no = models.CharField(max_length=255)
    is_current = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
