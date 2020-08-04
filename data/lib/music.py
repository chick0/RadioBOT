# -*- coding: utf-8 -*-

import logging

import eyed3


logger = logging.getLogger()


def get_data(item, user_upload=False):
    try:
        media = eyed3.load(item)
        artist = media.tag.artist
        title = media.tag.title

        if artist is None:
            logger.warning(f"Missing artist in [{item}]")
            artist = "None"
        if title is None:
            logger.warning(f"Missing Title in [{item}]")
            title = "None"
        return {'artist': artist, 'title': title, 'name': item, 'user_upload': user_upload}
    except AttributeError:
        logger.warning(f"Fail to get data from [{item}]")
