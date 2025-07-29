from typing import List

from src.models import Dependencies


class DependencyCollector:
    def __init__(self):
        self.dependencies: List[Dependencies] = []

    async def detect(self, dep: Dependencies):
        if not any(d.address == dep.address and d.port == dep.port for d in self.dependencies):
            self.dependencies.append(dep)

            await Dependencies.get_or_create(
                name=dep.name,
                app_name=dep.app_name,
                type=dep.type,
                source=dep.source,
                is_active=True,
                address=dep.address,
                port=dep.port
            )

    async def list(self):
        return self.dependencies


collector = DependencyCollector()
