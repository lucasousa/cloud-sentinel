import time
from functools import wraps

import redis.asyncio as redis

from src.core.collector import collector
from src.core.prometheus import metrics
from src.models.models import Dependencies, SLAReport


def patch_redis():
    original_execute_command = redis.Redis.execute_command

    @wraps(original_execute_command)
    async def patched_execute_command(self, *args, **kwargs):
        command = args[0] if args else "UNKNOWN"
        key = args[1] if len(args) > 1 else None
        dep_name = "redis"

        await collector.detect(Dependencies(
            name=dep_name,
            type="redis",
            address=args[0] if isinstance(args[0], str) else "localhost",
            port=6379,
            source="redis"
        ))

        start = time.monotonic()
        try:
            result = await original_execute_command(self, *args, **kwargs)
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
            #print(f"[Redis] ✅ {command} {key} ({duration:.4f}s)")
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
            #print(f"[Redis] ❌ {command} {key} FAILED ({duration:.4f}s): {e}")

    redis.Redis.execute_command = patched_execute_command
