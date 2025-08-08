import logging, sys, os
from pythonjsonlogger import jsonlogger

def setup_logging(env: str = "prod") -> None:
    handler = logging.StreamHandler(sys.stdout)
    fmt = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(logging.INFO if env == "prod" else logging.DEBUG)
    root.handlers.clear()
    root.addHandler(handler)

    # Reduce noise from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
