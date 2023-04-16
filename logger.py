import logging


def get_logger(name):
    """
    Returns a logger object configured with a console handler and a file handler.
    The console handler prints log messages to the console with level DEBUG or higher.
    The file handler saves log messages to a file named 'logfile.log' with level DEBUG or higher.
    The logger object can be used to write log messages for the given name.

    Parameters:
    name (str): The name of the logger object.

    Returns:
    logging.Logger: The configured logger object.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create file handler
    fh = logging.FileHandler("logfile.log")
    fh.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
