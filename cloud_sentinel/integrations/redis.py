import time
from functools import wraps

import psutil
import redis.asyncio as redis

from cloud_sentinel.core.enums import EventCode
from cloud_sentinel.core.kinesis import EventPublisher
from cloud_sentinel.core.prometheus import metrics
from cloud_sentinel.settings import APPLICATION_NAME


def patch_redis():
    original_execute_command = redis.Redis.execute_command

    @wraps(original_execute_command)
    async def patched_execute_command(self, *args, **kwargs):
        command = args[0] if args else "UNKNOWN"
        key = args[1] if len(args) > 1 else None
        dep_name = "redis"

        host = self.connection_pool.connection_kwargs.get("host", "unknown")
        port = self.connection_pool.connection_kwargs.get("port", 6379)

        event_publisher = EventPublisher()
        event_publisher.start_worker()

        dependence_data = dict(
            app_name=APPLICATION_NAME,
            name=dep_name,
            type="redis",
            address=host,
            port=port,
            source="redis",
        )
        await event_publisher.publish_event(
            user_id=f"{dep_name}-{host}",
            event_code=EventCode.DEPENDENCE.value,
            data=dependence_data,
        )

        start = time.monotonic()
        try:
            result = await original_execute_command(self, *args, **kwargs)
            duration = time.monotonic() - start
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            metrics.observe_success(dep_name, duration, cpu, mem)

            data = dict(
                app_name=APPLICATION_NAME,
                dependence_name=dep_name,
                dependence_address=f"{host}:{port}",
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name),
                cpu=cpu,
                memory=mem,
            )
            await event_publisher.publish_event(
                user_id=f"{dep_name}-{host}",
                event_code=EventCode.SLA_DATA.value,
                data=data,
            )
            print(f"[Redis] ✅ {command} {key} ({duration:.4f}s)")
            return result

        except Exception as e:
            duration = time.monotonic() - start
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            metrics.observe_failure(dep_name, duration, cpu, mem)

            data = dict(
                app_name=APPLICATION_NAME,
                dependence_name=dep_name,
                dependence_address=f"{host}:{port}",
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name),
                cpu=cpu,
                memory=mem,
            )
            await event_publisher.publish_event(
                user_id=f"{dep_name}-{host}",
                event_code=EventCode.SLA_DATA.value,
                data=data,
            )
            print(f"[Redis] ❌ {command} {key} FAILED ({duration:.4f}s): {e}")

    redis.Redis.execute_command = patched_execute_command
