from logging.config import dictConfig

from api.core.config import settings


def configure_logging() -> None:
    default_level = "DEBUG" if settings.fastapi_env == "development" else "INFO"
    level = (settings.log_level or default_level).upper()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    # "class": "logging.Formatter",
                     "()": "colorlog.ColoredFormatter",
                    "format": "%(log_color)s%(asctime)s -  %(name)s:%(lineno)d - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "log_colors": {
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "bold_red",
                    },
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
                "api": { "handlers": ["default"], "level": level, "propagate": False },
                "databases": { "handlers": ["default"], "level": "WARNING" }
            }
        }
    )