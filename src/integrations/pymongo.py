import functools


def patch_pymongo():
    try:
        import pymongo

        from core.collector import (
            Dependency,
            collector,
            dependency_latency,
            dependency_response_time,
        )

        original_init = pymongo.MongoClient.__init__

        @functools.wraps(original_init)
        def patched_init(self, *args, **kwargs):
            result = original_init(self, *args, **kwargs)
            if hasattr(self, 'address'):
                host, port = self.address
                dep = Dependency(
                    name="mongodb",
                    type="mongodb",
                    address=host,
                    port=port,
                    source="pymongo"
                )
                collector.detect(dep)
            return result

        pymongo.MongoClient.__init__ = patched_init
    except ImportError:
        pass
