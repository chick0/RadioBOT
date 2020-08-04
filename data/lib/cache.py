# -*- coding: utf-8 -*-

import os
import logging

logger = logging.getLogger()


def run():
    lists = os.listdir("data/")

    for item in lists:
        if item.find(".") is not -1:
            if item.startswith("cache__"):
                try:
                    os.remove(os.path.join("data", item))
                    logger.info(f"{item} is removed")
                except Exception as e:
                    logger.warning(f"Fail to remove cache file '{item}'")
                    logger.warning(f"-> detail: {e.__class__.__name__}: {e}")
