from typing import List

from prometheus_client import Counter, Gauge, Histogram, Summary
from pydantic import BaseModel


class Dependency(BaseModel):
    name: str
    type: str
    address: str
    port: int
    source: str


class DependencyCollector:
    def __init__(self):
        self.dependencies: List[Dependency] = []

    def detect(self, dep: Dependency):
        if not any(d.address == dep.address and d.port == dep.port for d in self.dependencies):
            self.dependencies.append(dep)
            print(f"Nova dependência detectada: {dep}")
            dependency_availability.labels(name=dep.name).set(1)

    def list(self):
        return self.dependencies


collector = DependencyCollector()

dependency_availability = Gauge('dependency_availability', 'Disponibilidade das dependências', ['name'])
dependency_response_time = Histogram('dependency_response_time_seconds', 'Tempo de resposta por dependência', ['name'])
dependency_throughput = Counter('dependency_throughput_total', 'Número de chamadas por dependência', ['name'])
dependency_latency = Summary('dependency_latency_seconds', 'Latência estimada por dependência', ['name'])
dependency_rtt = Summary('dependency_rtt_seconds', 'Round-trip time estimado por dependência', ['name'])
