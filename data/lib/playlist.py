# -*- coding: utf-8 -*-

import os
import json
import logging

import option
from data.lib import music

logger = logging.getLogger()


def get_playlist():
    playlist = list()

    logger.info(f"Loading music from Music Directory...")

    music_files = os.listdir(option.music_dir)
    logger.info(f"File Detected: {len(music_files)}")
    for music_file in music_files:
        try:
            data = music.get_data(item=os.path.join(option.music_dir, music_file),
                                  user_upload=False)

            if data is not None:
                playlist.append(data)
        except Exception as e:
            logger.warning(f"Fail to load music from [{music_file}]")
            logger.warning(f"Detail: {e}")

    try:
        logger.info("Testing User Upload Directory")
        with open("./data/user_upload/test", "w") as upload_directory_test:
            upload_directory_test.write("Hello, World")
            logger.info("OK! - Upload Directory Alive")

        music_files = os.listdir("./data/user_upload/")
        for music_file in music_files:
            data = music.get_data(item=os.path.join("data", "user_upload", music_file),
                                  user_upload=False)
            if data is not None:
                playlist.append(data)
    except FileNotFoundError:
        logger.info("SKIP - User Upload Directory is missing")

    try:
        def get_titles(lists):
            return lists['title']

        playlist = sorted(playlist, key=get_titles)
    except TypeError:
        logger.warning("Fail to sort playlist!!")

    if len(playlist) == 0:
        logger.warning("Playlist is EMPTY!")
    else:
        logger.info(f"OK! - Music is Ready! [+ {len(playlist)}]")

    with open("data/cache__playlist.json", "w") as pl_w:
        pl_w.write(json.dumps(playlist))

    return playlist
