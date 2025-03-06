import json
import logging

import faust
from opentelemetry._logs import set_logger_provider

# 1) Import OpenTelemetry Logs SDK
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.resources import Resource

# Tạo Resource với tên service "faust-logs"
resource = Resource.create({"service.name": "faust-logs"})

# 2) Tạo LoggerProvider và cấu hình Resource (nếu muốn)
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

# 3) Tạo exporter để gửi logs đi (OTLP)
otlp_exporter = OTLPLogExporter(
    endpoint="http://localhost:4317",
    insecure=True,
)


# 4) Thêm LogRecordProcessor vào LoggerProvider
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

# 5) Tạo LoggingHandler để bridge logs
otel_handler = LoggingHandler(
    level=logging.INFO, logger_provider=logger_provider
)

# Attach OTLP handler to root logger
# logging.getLogger().addHandler(otel_handler)

# Tạo logger và gửi log test
# Cấu hình logging rõ ràng trước khi Faust chạy

# Tạo và cấu hình logger gốc
logger = logging.getLogger("faust-logs-root")
logger.setLevel(logging.INFO)
logger.addHandler(otel_handler)


app = faust.App("hit_counter", broker="kafka://localhost:29092")


class hitCount(faust.Record, validation=True):
    hits: int
    timestamp: float
    userId: str


hit_topic = app.topic("hit_count", value_type=hitCount)
count_topic = app.topic(
    "count_topic", internal=True, partitions=1, value_type=hitCount
)

hits_table = app.Table("hitCount", default=int)
count_table = app.Table(
    "major-count", key_type=str, value_type=int, partitions=1, default=int
)


@app.agent(hit_topic)
async def count_hits(counts):
    async for count in counts:
        # Chuyển object `count` thành JSON string để log đầy đủ
        count_data = json.dumps(count.asdict(), ensure_ascii=False)
        logger.info(f"Data recieved is {count_data}")
        if count.hits > 20:
            await count_topic.send(value=count)


@app.agent(count_topic)
async def increment_count(counts):
    async for count in counts:
        # logger1 = logging.getLogger("faust-logs-root.agent1")
        count_data = json.dumps(count.asdict(), ensure_ascii=False)
        logger.info(f"Count in internal topic is {count_data}")
        count_table[str(count.userId)] += 1
        logger.info(
            f"{str(count.userId)} has now been seen {count_table[str(count.userId)]} times"
        )
