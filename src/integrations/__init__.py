from .boto3 import patch_boto3
from .patch_redis import patch_redis
from .pymongo import patch_pymongo
from .socket import patch_socket
from .sqlite import patch_tortoise_sqlite
from .vm import collect_vm_metrics_and_report


def patch_all_integrations():
    collect_vm_metrics_and_report()
    patch_tortoise_sqlite()
    patch_redis()
    patch_socket()
    patch_pymongo()
    patch_boto3()
