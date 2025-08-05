import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import boto3
import pytz

from src.settings import (
    AWS_KEY,
    AWS_SECRET,
    KINESIS_ENDPOINT_URL,
    KINESIS_EVENTS_STREAM_NAME,
    KINESIS_EVENTS_STREAM_REGION,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, timezone: str = "America/Fortaleza"):
        self.stream_name = KINESIS_EVENTS_STREAM_NAME
        self.region_name = KINESIS_EVENTS_STREAM_REGION
        self.timezone = pytz.timezone(timezone)
        self.queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor()
        self.client = boto3.client(
            "kinesis", 
            region_name=self.region_name,
            endpoint_url=KINESIS_ENDPOINT_URL,
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET
        )
        self._worker_task = None

    def start_worker(self):
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())

    async def publish_event(self, user_id: str, event_code: str, data: dict = {}):
        now = datetime.now(self.timezone)

        event = {
            "user_id": user_id,
            "event_code": event_code,
            "data": data,
            "created_at": now.isoformat()
        }

        await self.queue.put(event)

    async def _worker(self):
        while True:
            event = await self.queue.get()
            try:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._send_record,
                    event
                )
            except Exception as e:
                logger.info(f"[EventPublisher] Failed to send event: {e}")
            finally:
                self.queue.task_done()

    def _send_record(self, event: dict):
        self.client.put_record(
            StreamName=self.stream_name,
            Data=json.dumps(event),
            PartitionKey=str(event["user_id"])
        )
