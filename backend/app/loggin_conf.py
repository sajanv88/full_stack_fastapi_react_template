from logging.config import dictConfig

def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "format": "%(asctime)s -  %(name)s:%(lineno)d - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                    "level": "DEBUG"
                }
            },
            "loggers": {
                "uvicorn" : { "handlers": ["default"], "level": "INFO" },
                "app": { "handlers": ["default"], "level": "DEBUG", "propagate": False },
                "databases": { "handlers": ["default"], "level": "WARNING" }
            }
        }
    )