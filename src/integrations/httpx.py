def patch_httpx():
    try:
        import httpx

        from core.collector import (
            Dependency,
            collector,
            dependency_latency,
            dependency_response_time,
            dependency_throughput,
        )

        original_send = httpx.Client.send

        def send(self, request, **kwargs):
            host = request.url.host
            port = request.url.port or (443 if request.url.scheme == "https" else 80)
            dep = Dependency(
                name=host,
                type="http",
                address=host,
                port=port,
                source="httpx"
            )
            collector.detect(dep)
            dependency_throughput.labels(name=host).inc()
            with dependency_response_time.labels(name=host).time():
                with dependency_latency.labels(name=host).time():
                    return original_send(self, request, **kwargs)

        httpx.Client.send = send
    except ImportError:
        pass
