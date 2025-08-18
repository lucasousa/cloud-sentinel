import contextvars
import time
from functools import wraps

from tortoise.backends.sqlite.client import SqliteClient

from src.core.collector import collector
from src.core.prometheus import metrics
from src.models.models import Dependencies, SLAReport

_in_patch = contextvars.ContextVar("in_patch", default=False)


def patch_tortoise_sqlite():
    original_execute_query = SqliteClient.execute_query

    @wraps(original_execute_query)
    async def patched_execute_query(self, query, *args, **kwargs):
        if _in_patch.get():
            return await original_execute_query(self, query, *args, **kwargs)

        token = _in_patch.set(True)
        dep_name = "sqlite"
        db_path = getattr(self, "filename", "unknown.sqlite")

        try:
            await collector.detect(Dependencies(
                name=dep_name,
                type="sqlite",
                address=db_path,
                port=0,
                source="tortoise_sqlite"
            ))

            start = time.monotonic()
            result = await original_execute_query(self, query, *args, **kwargs)
            duration = time.monotonic() - start

            metrics.observe_success(dep_name, duration)

            await SLAReport.create(
                dependency=await Dependencies.get(name=dep_name),
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name)
            )
            return result

        except Exception as e:
            duration = time.monotonic() - start
            metrics.observe_failure(dep_name, duration)

            await SLAReport.create(
                dependency=await Dependencies.get(name=dep_name),
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name)
            )
            raise

        finally:
            _in_patch.reset(token)

    SqliteClient.execute_query = patched_execute_query
