import logging
from os import PathLike


def create_logger(
        name: str,
        file_path: str | PathLike[str] = None
) -> logging.Logger:
    custom_logger = logging.getLogger(name)

    if file_path is not None:
        # create file handler which logs even info messages
        fh = logging.FileHandler(file_path)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s \n%(message)s'))
        custom_logger.addHandler(fh)
        custom_logger.propagate = False

    return custom_logger


error_logger = create_logger('Error log')
db_logger = create_logger('Database log')
