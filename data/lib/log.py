# -*- coding: utf-8 -*-

import os
import time
import logging

logger = logging.getLogger()


def __clean_old_log(boot_time):
    log_files = os.listdir("./log")
    if len(log_files) > 1:
        logger.info("Moving Old Log...")
        try:
            for item in log_files:
                if item != f"{boot_time}.log":
                    logger.info(f"old_log: {item}")
                    os.rename(f"./log/{item}", f"./log/old/{item}")
                    logger.info(f"OK! - Old log moved -> {item}")
        except FileNotFoundError:
            os.mkdir("./log/old/")
            for item in log_files:
                if item != f"{boot_time}.log":
                    logger.info(f"old_log: {item}")
                    os.rename(f"./log/{item}", f"./log/old/{item}")
                    logger.info(f"OK! - Old log moved -> {item}")
        except Exception as e:
            logger.error(f"FAIL - {e}")


def create_logger():
    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    logger.setLevel(logging.INFO)

    boot_time = time.strftime("%Y-%m-%d %HH %MM", time.localtime(time.time()))
    try:
        file_handler = logging.FileHandler(f"log/{boot_time}.log")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    except FileNotFoundError:
        os.mkdir("log/")
        file_handler = logging.FileHandler(f"log/{boot_time}.log")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    del console_handler
    del file_handler

    __clean_old_log(boot_time)
