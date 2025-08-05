from .httpx import patch_httpx
from .postgres import patch_tortoise_postgres
from .vm import collect_vm_metrics_and_report


async def patch_all_integrations():
    patch_httpx()
    await collect_vm_metrics_and_report()
    patch_tortoise_postgres()
