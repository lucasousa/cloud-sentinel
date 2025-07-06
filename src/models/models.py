import datetime

from fastapi_admin.models import AbstractAdmin
from tortoise import Model, fields

from src.utils.enums import UnitType


class Admin(AbstractAdmin):
    last_login = fields.DatetimeField(description="Last Login", default=datetime.datetime.now)
    email = fields.CharField(description="E-mail",  max_length=200, default="")
    avatar = fields.CharField(max_length=200, default="", description="Avatar URL")
    intro = fields.TextField(default="", description="Introduction text")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}#{self.username}"


class MonitoredMetric(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True, description="Name")
    unit = fields.IntEnumField(UnitType, description="Unit of measurement")
    is_active = fields.BooleanField(default=True, description="Is the metric active?")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class Sla(Model):
    id = fields.IntField(pk=True)
    metric = fields.ForeignKeyField("models.MonitoredMetric", related_name="slas")
    min_threshold = fields.FloatField(description="Minimum threshold for SLA")
    max_threshold = fields.FloatField(description="Maximum threshold for SLA")
    is_active = fields.BooleanField(default=True, description="Is the SLA active?")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"SLA: {self.name}"
