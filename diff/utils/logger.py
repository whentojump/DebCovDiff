import logging

def config_logger(level=logging.ERROR):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)-25s - %(levelname)-8s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def get_logger(name="diff.py"):
    logger = logging.getLogger(name)
    return logger
