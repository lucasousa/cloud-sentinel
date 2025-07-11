from .boto3 import patch_boto3
from .httpx import patch_httpx
from .patch_redis import patch_redis
from .pymongo import patch_pymongo
from .socket import patch_socket


def patch_all_integrations():
    patch_redis()
    patch_httpx()
    patch_socket()
    patch_pymongo()
    patch_boto3()
