from fastapi_admin.widgets import displays
from starlette.requests import Request

from src.models import MonitoredMetric  # ajuste o import conforme necessário


class MetricNameDisplay(displays.Display):
    async def render(self, request: Request, value):
        if not value:
            return await super().render(request, "-")
        metric = await MonitoredMetric.get_or_none(id=value)
        if metric:
            return await super().render(request, metric.name)
        return await super().render(request, "-")

