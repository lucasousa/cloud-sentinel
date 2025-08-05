import time
from functools import wraps

import psutil
import redis.asyncio as redis

from src.core.collector import collector
from src.core.kinesis import EventPublisher
from src.core.prometheus import metrics
from src.models.models import Dependencies, SLAReport
from src.settings import APPLICATION_NAME


def patch_redis():
    original_execute_command = redis.Redis.execute_command

    @wraps(original_execute_command)
    async def patched_execute_command(self, *args, **kwargs):
        command = args[0] if args else "UNKNOWN"
        key = args[1] if len(args) > 1 else None
        dep_name = "redis"

        await collector.detect(
            Dependencies(
                app_name=APPLICATION_NAME,
                name=dep_name,
                type="redis",
                address="localhost",
                port=6379,
                source="redis",
            )
        )

        start = time.monotonic()
        try:
            result = await original_execute_command(self, *args, **kwargs)
            duration = time.monotonic() - start
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            metrics.observe_success(dep_name, duration, cpu, mem)
            await SLAReport.create(
                dependency=await Dependencies.get(name=dep_name),
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name),
                cpu=cpu,
                memory=mem,
            )
            print(f"[Redis] ✅ {command} {key} ({duration:.4f}s)")
            # event_publisher = EventPublisher()
            # event_publisher.start_worker()
            # await event_publisher.publish_event(
            #     user_id="system",
            #     platform="redis",
            #     service="redis",
            #     event_code="command_executed",
            #     metadata={"command": command, "key": key},
            #     data={"duration": duration}
            # )
            return result
        except Exception as e:
            duration = time.monotonic() - start
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            metrics.observe_failure(dep_name, duration, cpu, mem)
            await SLAReport.create(
                dependency=1,  # await Dependencies.get(name=dep_name),
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name),
                cpu=cpu,
                memory=mem,
            )
            print(f"[Redis] ❌ {command} {key} FAILED ({duration:.4f}s): {e}")

    redis.Redis.execute_command = patched_execute_command
