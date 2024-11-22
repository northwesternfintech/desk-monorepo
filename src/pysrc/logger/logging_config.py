import logging
import logging.config
import os
from datetime import datetime

log_dir = "logs/"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def setup_logging() -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": "INFO",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": log_file,  
                    "formatter": "standard",
                    "level": "DEBUG",
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
            },
        }
    )
