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
        return self.name


class Sla(Model):
    id = fields.IntField(pk=True)
    metric = fields.ForeignKeyField("models.MonitoredMetric", related_name="slas")
    min_threshold = fields.FloatField(description="Minimum threshold for SLA")
    max_threshold = fields.FloatField(description="Maximum threshold for SLA")
    is_active = fields.BooleanField(default=True, description="Is the SLA active?")
    created_at = fields.DatetimeField(auto_now_add=True)

    @property
    def metric_name(self):
        return self.metric.name if self.metric else None

    def __str__(self):
        return f"SLA: {self.name}"


class Dependencies(Model):
    id = fields.IntField(pk=True)
    app_name = fields.CharField(max_length=100, description="Application name", blank=True, null=True)
    name = fields.CharField(max_length=100, description="Name")
    type = fields.CharField(max_length=50, description="Type", blank=True, null=True)
    address = fields.CharField(max_length=200, description="Address", blank=True, null=True)
    port = fields.IntField(description="Port", blank=True, null=True)
    source = fields.CharField(max_length=100, description="Source", blank=True, null=True)
    is_active = fields.BooleanField(default=True, description="Is active?")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SLAReport(Model):
    id = fields.IntField(pk=True)
    app_name = fields.CharField(max_length=100, description="Application name", blank=True, null=True)
    dependency = fields.ForeignKeyField(
        "models.Dependencies",
        related_name="sla_reports",
        on_delete=fields.CASCADE
    )
    timestamp = fields.DatetimeField(auto_now_add=True)
    availability = fields.FloatField(null=True)
    latency = fields.FloatField(null=True)
    response_time = fields.FloatField(null=True)
    rtt = fields.FloatField(null=True)
    throughput = fields.IntField(null=True)
    cpu = fields.FloatField(null=True)
    memory = fields.FloatField(null=True)

    class Meta:
        table = "sla_report"


class MonitoringAggregationTime(Model):
    id = fields.IntField(pk=True)
    window_size = fields.IntField(description="Slice de tempo do monitoramento")
