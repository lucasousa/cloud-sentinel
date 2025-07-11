from typing import List

from prometheus_client import Counter, Gauge, Histogram, Summary

from src.models import Dependencies


class DependencyCollector:
    def __init__(self):
        self.dependencies: List[Dependencies] = []  

    async def detect(self, dep: Dependencies):
        print(f"Detectando dependência: {dep.name} ({dep.type}) - {dep.address}:{dep.port}")
        if not any(d.address == dep.address and d.port == dep.port for d in self.dependencies):
            self.dependencies.append(dep)

            await Dependencies.get_or_create(
                defaults={
                    "name": dep.name,
                    "type": dep.type,
                    "source": dep.source,
                    "is_active": True
                },
                address=dep.address,
                port=dep.port,
            )

    async def list(self):
        return self.dependencies


collector = DependencyCollector()

dependency_availability = Gauge('dependency_availability', 'Disponibilidade das dependências', ['name'])
dependency_response_time = Histogram('dependency_response_time_seconds', 'Tempo de resposta por dependência', ['name'])
dependency_throughput = Counter('dependency_throughput_total', 'Número de chamadas por dependência', ['name'])
dependency_latency = Summary('dependency_latency_seconds', 'Latência estimada por dependência', ['name'])
dependency_rtt = Summary('dependency_rtt_seconds', 'Round-trip time estimado por dependência', ['name'])
