from decouple import config

APPLICATION_NAME = config("APPLICATION_NAME", cast=str, default="")

KINESIS_ENDPOINT_URL = config("KINESIS_ENDPOINT_URL", cast=str, default="http://localhost:4566")
KINESIS_EVENTS_STREAM_REGION = config("KINESIS_EVENTS_STREAM_REGION", cast=str, default="us-east-1")
KINESIS_EVENTS_STREAM_NAME = config("KINESIS_EVENTS_STREAM_NAME", cast=str, default="cloud-sentinel")
AWS_KEY = config("AWS_KEY", cast=str, default="temp")
AWS_SECRET = config("AWS_SECRET", cast=str, default="temp")