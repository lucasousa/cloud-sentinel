import contextvars
import time
from functools import wraps

import psutil
from tortoise.backends.asyncpg.client import AsyncpgDBClient

from cloud_sentinel.core.enums import EventCode
from cloud_sentinel.core.kinesis import EventPublisher
from cloud_sentinel.core.prometheus import metrics
from cloud_sentinel.settings import APPLICATION_NAME

_in_patch = contextvars.ContextVar("in_patch", default=False)


def patch_tortoise_postgres():
    methods_to_patch = [
        "execute_query",
        "execute_query_dict",
    ]

    for method_name in methods_to_patch:
        original_method = getattr(AsyncpgDBClient, method_name)

        @wraps(original_method)
        async def patched_method(
            self, query, *args, __original=original_method, **kwargs
        ):
            if _in_patch.get():
                return await __original(self, query, *args, **kwargs)

            token = _in_patch.set(True)
            dep_name = "postgres"
            event_publisher = EventPublisher()
            event_publisher.start_worker()
            print("host ", self.host, self.port)
            if hasattr(self, "host") and hasattr(self, "port"):
                db_address = f"{self.host}:{self.port}"
                await event_publisher.publish_event(
                    user_id=f"{dep_name}-{self.host}",
                    event_code=EventCode.DEPENDENCE.value,
                    data=dict(
                        name=dep_name,
                        app_name=APPLICATION_NAME,
                        type="postgres",
                        address=db_address,
                        port=self.port,
                        source="tortoise_postgres",
                    ),
                )
            try:
                start = time.monotonic()
                result = await __original(self, query, *args, **kwargs)
                duration = time.monotonic() - start
                cpu_percent = psutil.cpu_percent(interval=0.5)
                memory_percent = psutil.virtual_memory().percent
                metrics.observe_success(dep_name, duration, cpu_percent, memory_percent)

                event_data = dict(
                    dependence_name=dep_name,
                    app_name=APPLICATION_NAME,
                    dependence_address=db_address,
                    availability=metrics.get_availability(dep_name),
                    latency=duration,
                    response_time=duration,
                    rtt=duration,
                    throughput=metrics.get_throughput(dep_name),
                    cpu=cpu_percent,
                    memory=memory_percent,
                )
                await event_publisher.publish_event(
                    user_id=f"{dep_name}-{db_address}",
                    event_code=EventCode.SLA_DATA.value,
                    data=event_data,
                )
                return result

            except Exception:
                duration = time.monotonic() - start
                cpu_percent = psutil.cpu_percent(interval=0.5)
                memory_percent = psutil.virtual_memory().percent
                metrics.observe_failure(dep_name, duration, cpu_percent, memory_percent)

                event_data = dict(
                    app_name=APPLICATION_NAME,
                    dependence_name=dep_name,
                    dependence_address=db_address,
                    availability=metrics.get_availability(dep_name),
                    latency=duration,
                    response_time=duration,
                    rtt=duration,
                    throughput=metrics.get_throughput(dep_name),
                    cpu=cpu_percent,
                    memory=memory_percent,
                )
                await event_publisher.publish_event(
                    user_id=f"{dep_name}-{db_address}",
                    event_code=EventCode.SLA_DATA.value,
                    data=event_data,
                )
                return result

            finally:
                _in_patch.reset(token)

        setattr(AsyncpgDBClient, method_name, patched_method)
