import contextvars
import time
from functools import wraps

import psutil
from tortoise.backends.asyncpg.client import AsyncpgDBClient

from src.core.collector import collector
from src.core.prometheus import metrics
from src.models.models import Dependencies, SLAReport
from src.settings import APPLICATION_NAME

_in_patch = contextvars.ContextVar("in_patch", default=False)


def patch_tortoise_postgres():
    original_execute_query = AsyncpgDBClient.execute_query

    @wraps(original_execute_query)
    async def patched_execute_query(self, query, *args, **kwargs):
        if _in_patch.get():
            return await original_execute_query(self, query, *args, **kwargs)

        token = _in_patch.set(True)
        dep_name = "postgres"
        db_address = f"{self.host}:{self.port}"

        try:
            await collector.detect(Dependencies(
                name=dep_name,
                app_name=APPLICATION_NAME,
                type="postgres",
                address=db_address,
                port=self.port,
                source="tortoise_postgres"
            ))

            start = time.monotonic()
            result = await original_execute_query(self, query, *args, **kwargs)
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
                memory=memory_percent
            )
            return result

        except Exception:
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
                memory=memory_percent
            )
            raise

        finally:
            _in_patch.reset(token)

    AsyncpgDBClient.execute_query = patched_execute_query
