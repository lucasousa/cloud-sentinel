import asyncio
import logging
import socket
import time

import psutil

from src.core.collector import collector
from src.core.prometheus import metrics
from src.models.models import Dependencies, SLAReport
from src.settings import APPLICATION_NAME

logger = logging.getLogger(__name__)


def collect_vm_metrics_and_report():
    loop = asyncio.get_event_loop()
    loop.create_task(_collect_vm_metrics_async())
    logger.info("Collecting vm metrics")


async def _collect_vm_metrics_async():
    host = socket.gethostname()
    dep_name = "vm"

    try:
        dep = Dependencies(
            app_name=APPLICATION_NAME,
            name=dep_name,
            type="vm",
            address=host,
            port=0,
            source=host,
        )

        await collector.detect(dep)
        start = time.monotonic()

        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent

            duration = time.monotonic() - start
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

            print(f"[vm-local] ✅ CPU {cpu:.1f}% | MEM {mem:.1f}% | ({duration:.4f}s)")

        except Exception as e:
            duration = time.monotonic() - start
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            metrics.observe_failure(dep_name, duration, cpu, mem)

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

            print(f"[vm-local] ❌ Erro: {e} ({duration:.4f}s)")

    except Exception as outer_error:
        print(f"[vm-local] ❌ Erro ao iniciar coleta de VM: {outer_error}")
