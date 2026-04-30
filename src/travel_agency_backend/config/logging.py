import logging
from contextvars import ContextVar


request_id_context: ContextVar[str] = ContextVar("request_id", default="unknown")


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def setup_logging() -> None:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s - (%(name)s - ID: %(request_id)s)"
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
