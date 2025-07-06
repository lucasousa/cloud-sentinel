import socket

from core.collector import Dependency, collector

_original_connect = socket.socket.connect

def patch_socket():
    def traced_connect(self, address):
        try:
            host, port = address
            dep = Dependency(
                name=host,
                type="socket",
                address=host,
                port=port,
                source="socket"
            )
            collector.detect(dep)
        except Exception as e:
            print(f"Erro na interceptação de socket: {e}")
        return _original_connect(self, address)

    socket.socket.connect = traced_connect
