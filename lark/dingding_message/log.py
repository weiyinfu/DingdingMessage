import colorlog
import logging

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s %(levelname)s %(pathname)s:%(lineno)s %(funcName)s %(name)s:%(message)s")
)


def get_logger(logger_name=None):
    logger = colorlog.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return colorlog.root


if __name__ == "__main__":
    log = get_logger()
    print(log.level, logging.INFO)
    log.info("haha")
