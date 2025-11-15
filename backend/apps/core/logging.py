import logging


class RequestIdFilter(logging.Filter):
    """
    Injects request_id into log records; defaults to '-'.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", "-")
        return True
