from .httpx import patch_httpx
from .postgres import patch_tortoise_postgres
from .redis import patch_redis
from .vm import collect_vm_metrics_and_report


async def patch_all_integrations():
    patch_redis()
    patch_httpx()
    await collect_vm_metrics_and_report()
    patch_tortoise_postgres()
