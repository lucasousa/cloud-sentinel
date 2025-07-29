from .patch_redis import patch_redis
from .postgres import patch_tortoise_postgres
from .vm import collect_vm_metrics_and_report


def patch_all_integrations():
    collect_vm_metrics_and_report()
    patch_redis()
    patch_tortoise_postgres()
