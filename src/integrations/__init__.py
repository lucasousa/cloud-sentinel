from .boto3 import patch_boto3
from .httpx import patch_httpx
from .pymongo import patch_pymongo
from .socket import patch_socket


def patch_all_integrations():
    patch_socket()
    patch_httpx()
    patch_pymongo()
    patch_boto3()
