from prometheus_client import Counter, Gauge, Histogram, Summary


class PrometheusMetrics:
    def __init__(self):
        self._availability = Gauge(
            'dependency_availability',
            'Disponibilidade das dependências',
            ['name']
        )
        self._response_time = Histogram(
            'dependency_response_time_seconds',
            'Tempo de resposta por dependência',
            ['name']
        )
        self._throughput = Counter(
            'dependency_throughput_total',
            'Número de chamadas por dependência',
            ['name']
        )
        self._latency = Summary(
            'dependency_latency_seconds',
            'Latência estimada por dependência',
            ['name']
        )
        self._rtt = Summary(
            'dependency_rtt_seconds',
            'Round-trip time estimado por dependência',
            ['name']
        )
        self.vm_cpu = Gauge("vm_cpu_usage_percent", "Uso de CPU da VM (em %)")
        self.vm_memory = Gauge("vm_memory_usage_percent", "Uso de memória da VM (em %)")

    def observe_success(self, name: str, duration: float, cpu: float, memory: float):
        self._availability.labels(name=name).set(1)
        self._throughput.labels(name=name).inc()
        self._response_time.labels(name=name).observe(duration)
        self._latency.labels(name=name).observe(duration)
        self._rtt.labels(name=name).observe(duration)
        self.vm_cpu.set(cpu)
        self.vm_memory.set(memory)

    def observe_failure(self, name: str, duration: float, cpu: float, memory: float):
        self._availability.labels(name=name).set(0)
        self._throughput.labels(name=name).inc()
        self._response_time.labels(name=name).observe(duration)
        self._latency.labels(name=name).observe(duration)
        self._rtt.labels(name=name).observe(duration)
        self.vm_cpu.set(cpu)
        self.vm_memory.set(memory)

    def get_throughput(self, name: str) -> int:
        for sample in self._throughput.collect():
            for s in sample.samples:
                if s.labels.get("name") == name:
                    return int(s.value)
        return 0

    def get_availability(self, name: str) -> float:
        for sample in self._availability.collect():
            for s in sample.samples:
                if s.labels.get("name") == name:
                    return float(s.value)
        return 0.0


metrics = PrometheusMetrics()
