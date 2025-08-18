import logging
import socket
import time

import psutil

from src.core.enums import EventCode
from src.core.kinesis import EventPublisher
from src.core.prometheus import metrics
from src.settings import APPLICATION_NAME

logger = logging.getLogger(__name__)


async def collect_vm_metrics_and_report():
    host = str(socket.gethostname())
    dep_name = "vm"
    event_publisher = EventPublisher()
    event_publisher.start_worker()

    try:
        dependence_data = dict(
            app_name=APPLICATION_NAME,
            name=dep_name,
            type="vm",
            address=host,
            port=0,
            source=host,
        )
        await event_publisher.publish_event(
            user_id=f"{dep_name}-{host}",
            event_code=EventCode.DEPENDENCE.value,
            data=dependence_data
        )
        start = time.monotonic()

        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent

            duration = time.monotonic() - start
            metrics.observe_success(dep_name, duration, cpu, mem)

            data = dict(
                dependence_name=dep_name,
                dependence_address=host,
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
                data=data
            )

            print(f"[vm-local] ✅ CPU {cpu:.1f}% | MEM {mem:.1f}% | ({duration:.4f}s)")

        except Exception as e:
            duration = time.monotonic() - start
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            metrics.observe_failure(dep_name, duration, cpu, mem)

            data = dict(
                dependence_name=dep_name,
                address=host,
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
                data=data
            )

            print(f"[vm-local] ❌ Erro: {e} ({duration:.4f}s)")

    except Exception as outer_error:
        print(f"[vm-local] ❌ Erro ao iniciar coleta de VM: {outer_error}")
