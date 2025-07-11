import inspect
import time
from functools import wraps

import redis.asyncio as redis

from src.core.collector import (
    collector,
    dependency_availability,
    dependency_latency,
    dependency_response_time,
    dependency_rtt,
    dependency_throughput,
)
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
            source="patch_redis"
        ))

        start = time.monotonic()
        try:
            result = await original_execute_command(self, *args, **kwargs)
            duration = time.monotonic() - start

            dependency_throughput.labels(dep_name).inc()
            dependency_response_time.labels(dep_name).observe(duration)
            dependency_latency.labels(dep_name).observe(duration)
            dependency_rtt.labels(dep_name).observe(duration)
            dependency_availability.labels(dep_name).set(1)
            
            await SLAReport.create(
                dependency=await Dependencies.get(name=dep_name),
                availability=1,
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=1
            )
            print(f"[Redis] ✅ {command} {key} ({duration:.4f}s)")
            return result
        except Exception as e:
            duration = time.monotonic() - start
            dependency_availability.labels(dep_name).set(0)
            dependency_latency.labels(dep_name).observe(duration)
            dependency_response_time.labels(dep_name).observe(duration)
            dependency_rtt.labels(dep_name).observe(duration)
            await SLAReport.create(
                dependency=await Dependencies.get(name=dep_name),
                availability=0,
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=0
            )
            print(f"[Redis] ❌ {command} {key} FAILED ({duration:.4f}s): {e}")
            raise

    redis.Redis.execute_command = patched_execute_command
