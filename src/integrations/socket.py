import socket

from src.core.collector import DependencyCollector, collector

_original_connect = socket.socket.connect


def patch_socket():
    def traced_connect(self, address):
        try:
            host, port = address
            dep = DependencyCollector(
                name=host,
                type="socket",
                address=host,
                port=port,
                source="socket"
            )
            collector.detect(dep)
        except Exception as e:
            pass
        return _original_connect(self, address)

    socket.socket.connect = traced_connect
