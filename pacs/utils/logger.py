from logging import DEBUG, FileHandler, Formatter, Logger, StreamHandler, getLogger


class CenteredFormatter(Formatter):
    def format(self, record):
        record.filename = record.filename.center(17)
        record.funcName = record.funcName.center(17)
        return super().format(record)


def generate_logger(logger_name: str, log_file: str = None) -> Logger:
    logger = getLogger(logger_name)

    logfmt = (
        "%(levelname)-9s  %(asctime)s  [%(filename)-17s - %(funcName)-17s] %(message)s"
    )
    datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = None
    if log_file is not None:
        file_handler = FileHandler(f"{log_file}", mode="a", encoding="utf-8")
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(CenteredFormatter(logfmt, datefmt=datefmt))
        logger.addHandler(file_handler)

    stream_handler = StreamHandler()
    stream_handler.setFormatter(CenteredFormatter(logfmt, datefmt=datefmt))
    logger.addHandler(stream_handler)
    logger.setLevel(DEBUG)

    logger.file_handler = file_handler

    return logger


def close_logger(logger):
    file_handler = getattr(logger, "file_handler", None)
    if file_handler is not None:
        file_handler.close()
