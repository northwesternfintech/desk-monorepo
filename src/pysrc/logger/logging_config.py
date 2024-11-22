import logging
import logging.config


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
                    "filename": "src/pysrc/logger/logs/project.log",
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
