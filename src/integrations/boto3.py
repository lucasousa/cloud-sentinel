def patch_boto3():
    try:
        import boto3

        from core.collector import Dependency, collector

        original_client = boto3.client

        def patched_client(service_name, *args, **kwargs):
            result = original_client(service_name, *args, **kwargs)
            if service_name == "dynamodb":
                region = kwargs.get("region_name", "us-east-1")
                dep = Dependency(
                    name="dynamodb",
                    type="aws_dynamodb",
                    address=f"dynamodb.{region}.amazonaws.com",
                    port=443,
                    source="boto3"
                )
                collector.detect(dep)
            return result

        boto3.client = patched_client
    except ImportError:
        pass
