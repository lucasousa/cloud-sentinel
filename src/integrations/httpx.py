import contextvars
import time
from functools import wraps

import httpx
import psutil

from src.core.collector import collector
from src.core.prometheus import metrics
from src.models.models import Dependencies, SLAReport
from src.settings import APPLICATION_NAME

_httpx_patch = contextvars.ContextVar("httpx_patch", default=False)


def patch_httpx():
    original_request = httpx.AsyncClient.request

    @wraps(original_request)
    async def patched_request(self, method, url, *args, **kwargs):
        if _httpx_patch.get():
            return await original_request(self, method, url, *args, **kwargs)

        token = _httpx_patch.set(True)
        try:
            parsed_url = httpx.URL(url)
            address = parsed_url.host
            port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
            dep_name = address
            await collector.detect(
                Dependencies(
                    name=dep_name,
                    app_name=APPLICATION_NAME,
                    type="http",
                    address=address,
                    port=port,
                    source="httpx",
                )
            )

            start = time.monotonic()
            response = await original_request(self, method, url, *args, **kwargs)
            duration = time.monotonic() - start

            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_percent = psutil.virtual_memory().percent
            metrics.observe_success(dep_name, duration, cpu_percent, memory_percent)

            await SLAReport.create(
                dependency=await Dependencies.get(name=dep_name),
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name),
                cpu=cpu_percent,
                memory=memory_percent,
            )

            return response

        except Exception as e:
            duration = time.monotonic() - start
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_percent = psutil.virtual_memory().percent
            metrics.observe_failure(dep_name, duration, cpu_percent, memory_percent)

            await SLAReport.create(
                dependency=await Dependencies.get(name=dep_name),
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name),
                cpu=cpu_percent,
                memory=memory_percent,
            )
            raise e

        finally:
            _httpx_patch.reset(token)

    httpx.AsyncClient.request = patched_request
