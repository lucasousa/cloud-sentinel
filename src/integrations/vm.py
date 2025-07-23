import asyncio
import socket
import time

import psutil

from src.core.collector import collector
from src.core.prometheus import metrics
from src.models.models import Dependencies, SLAReport


def collect_vm_metrics_and_report():
    asyncio.create_task(_collect_vm_metrics_async())


async def _collect_vm_metrics_async():
    dep_name = "vm"
    host = socket.gethostname()

    try:
        dep, _ = await Dependencies.get_or_create(
            name=dep_name,
            defaults={
                "type": "vm",
                "address": host,
                "port": 0,
                "source": "local"
            }
        )

        await collector.detect(dep)

        start = time.monotonic()

        try:
            # Coleta de métricas locais
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent

            duration = time.monotonic() - start

            # Atualiza métricas Prometheus
            metrics.vm_cpu.set(cpu)
            metrics.vm_memory.set(mem)
            metrics.vm_disk.set(disk)
            metrics.observe_success(dep_name, duration)

            await SLAReport.create(
                dependency=dep,
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name)
            )

            print(f"[vm-local] ✅ CPU {cpu:.1f}% | MEM {mem:.1f}% | DISK {disk:.1f}% ({duration:.4f}s)")

        except Exception as e:
            duration = time.monotonic() - start
            metrics.observe_failure(dep_name, duration)

            await SLAReport.create(
                dependency=dep,
                availability=metrics.get_availability(dep_name),
                latency=duration,
                response_time=duration,
                rtt=duration,
                throughput=metrics.get_throughput(dep_name)
            )

            print(f"[vm-local] ❌ Erro: {e} ({duration:.4f}s)")

    except Exception as outer_error:
        print(f"[vm-local] ❌ Erro ao iniciar coleta de VM: {outer_error}")
