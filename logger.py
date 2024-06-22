""" logger的文件 """

import logging
import colorlog

# 配置日志记录器
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "reset",
            "INFO": "cyan",
            "WARNING": "bold_yellow",
            "ERROR": "bold_red",
            "CRITICAL": "bold_red",
        },
        secondary_log_colors={},
        style="%",
    )
)

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
