from typing import Any

import uvicorn


def get_logger_config() -> dict[str, Any]:
    log_config = uvicorn.config.LOGGING_CONFIG

    # set message format
    log_config["formatters"]["access"]["fmt"] = (
        "%(levelprefix)s %(asctime)s | %(client_addr)s - "
        '"%(request_line)s" %(status_code)s'
    )
    log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    log_config["formatters"]["default"]["fmt"] = (
        "%(levelprefix)s %(asctime)s | [%(name)s:%(lineno)d] | %(message)s"
    )
    log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

    # add new handler to stdout
    log_config["handlers"]["application"] = {
        "formatter": "default",
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stdout",
    }

    # set root logger
    log_config["root"] = {
        "handlers": ["application"],
        "level": "INFO",
        "propagate": False,
    }

    # set a default dynamic logger
    log_config["loggers"]["__main__"] = {
        "handlers": ["application"],
        "level": "INFO",
        "propagate": False,
    }

    return log_config
