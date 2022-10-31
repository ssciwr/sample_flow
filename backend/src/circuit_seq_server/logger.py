from __future__ import annotations
import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(name)s  | [%(asctime)s %(levelname)s] %(message)s", "%H:%M:%S"
        )
    )
    logger.addHandler(handler)
    return logger
