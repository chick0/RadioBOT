# -*- coding: utf-8 -*-

import os
import time
import logging

logger = logging.getLogger()


def create_file_handler(log_formatter):
    boot_time = time.strftime("%Y-%m-%d %HH %MM", time.localtime(time.time()))
    try:
        file_handler = logging.FileHandler(f"log/{boot_time}.log")
        file_handler.setFormatter(log_formatter)
    except FileNotFoundError:
        os.mkdir("log/")
        file_handler = logging.FileHandler(f"log/{boot_time}.log")
        file_handler.setFormatter(log_formatter)

    return file_handler


def create_console_handler(log_formatter):
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    return console_handler


def create_logger():
    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(create_console_handler(log_formatter))
    logger.addHandler(create_file_handler(log_formatter))
