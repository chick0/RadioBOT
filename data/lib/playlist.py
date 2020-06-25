# -*- coding: utf-8 -*-

import os
import logging
import subprocess

try:
    import eyed3
except ModuleNotFoundError:
    print("===< Installing Module >===")
    subprocess.run(['pip', 'install', 'eyeD3==0.9.5'])
    print("===========================")
    import eyed3

import data.lib.option as option_loader

logger = logging.getLogger()


def get_playlist():
    playlist = list()
    option = option_loader.get_option()

    logger.info(f"Loading music from Music Directory...")
    try:
        music_files = os.listdir(option['music_dir'])
        for music_file in music_files:
            try:
                media = eyed3.load(option['music_dir'] + music_file)
                artist = media.tag.artist
                title = media.tag.title

                if artist is None:
                    logger.warning(f"Missing artist in [{music_file}]")
                    artist = "None"
                if title is None:
                    logger.warning(f"Missing Title in [{music_file}]")
                    title = "None"
                playlist.append({'artist': artist, 'title': title, 'name': music_file})
            except AttributeError:
                logger.warning(f"Fail to get data from [{music_file}]")
                logger.warning(f"Remove [{music_file}] from playlist")
        try:
            def get_titles(lists):
                return lists['title']

            playlist = sorted(playlist, key=get_titles)
        except TypeError:
            logger.warning("Fail to sort playlist!!")
        logger.info(f"OK! - Music is Ready! + {len(playlist)}")
    except Exception as e:
        logger.critical(f"FAIL - Fail to load music / {e}")
        logger.warning("Playlist is EMPTY!")

    return playlist
