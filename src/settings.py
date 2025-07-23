from decouple import config

APPLICATION_NAME = config("APPLICATION_NAME", cast=str, default="MyApp")
DATABASE_URL = config("DATABASE_URL", cast=str, default="")
REDIS_URL = config("REDIS_URL", cast=str, default="redis://localhost:6379/0")
KINESIS_ENDPOINT_URL = config("KINESIS_ENDPOINT_URL", cast=str, default="http://localhost:4566")
KINESIS_EVENTS_STREAM_REGION = config("KINESIS_EVENTS_STREAM_REGION", cast=str, default="us-east-1")
KINESIS_EVENTS_STREAM_NAME = config("KINESIS_EVENTS_STREAM_NAME", cast=str, default="cloud-sentinel")