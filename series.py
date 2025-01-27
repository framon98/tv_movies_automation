from os.path import join
from os import listdir, rmdir
from shutil import move
import shutil
import os
from tkinter.constants import NONE
import patoolib
import py7zr
import logging
import coloredlogs
import re
import time
import rarfile
import yaml

# ----Logging config----#
logger = logging.getLogger("SeriesOrganizer")
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('errors.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.ERROR)

# Formatters
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
# Handlers
logger.addHandler(c_handler)
logger.addHandler(f_handler)
logger.setLevel(logging.DEBUG)
coloredlogs.install(level=logging.DEBUG, logger=logger, fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s')


class Tvseries:
    def __init__(self):
        self.src_dir = ""
        self.dst_dir = ""

    def set_dirs(self, src, dst="", same_dir=False):
        logger.debug("Setting directories for source and destination")
        self.src_dir = os.path.normpath(src)
        logger.debug("Source directory is: {}".format(self.src_dir))
        if same_dir:
            self.dst_dir = self.src_dir
        else:
            self.dst_dir = os.path.normpath(dst)
        logger.debug("Destination directory is: {}".format(self.dst_dir))

    def extract_files(self):
        for zipfile in listdir(self.src_dir):
            if zipfile[-4:] == '.rar':
                logger.info("Extracting {}".format(zipfile))
                compr_file = rarfile.RarFile(join(self.src_dir, zipfile))
                compr_file.extractall(self.src_dir)
                logger.debug("Closing...")
                compr_file.close()
                logger.debug("Erasing compressed file {}".format(join(self.src_dir, zipfile)))
                os.remove(join(self.src_dir, zipfile))
            elif zipfile[-4:] == '.zip':
                logger.info("Extracting {}".format(zipfile))
                compr_file = patoolib.extract_archive(join(self.src_dir, zipfile), outdir=self.src_dir)
                logger.debug("Closing...")
                logger.debug("Erasing compressed file {}".format(join(self.src_dir, zipfile)))
                os.remove(join(self.src_dir, zipfile))
            else:
                logger.error("File {} is not a rar file".format(zipfile))

    def move_files(self):
        for zipfile in listdir(self.src_dir):
            if os.path.isdir(join(self.src_dir, zipfile)):
                logger.warning("{} is a directory and cannot be moved".format(zipfile))
                continue 
            elif zipfile[-4:] == '.mkv':
                # logger.debug(zipfile)
                logger.info("Moving to {}".format(self.dst_dir))
                move(join(self.src_dir, zipfile), join(self.dst_dir, zipfile))
            else:
                logger.error("File {} is not compatible".format(zipfile))

    def change_names(self):
        for episode in listdir(self.src_dir):
            if os.path.isdir(join(self.src_dir, episode)):
                logger.warning("{} is a directory and cannot be renamed".format(episode))
                continue
            try:
                # epi = re.search(r"(^.*?)1080.*?-(.*?.mkv)", episode)
                if re.search(r"(S\d\dE\d\d)", episode) is not None:
                    
                    logger.info("Waiting for 3 seconds...")
                    time.sleep(3)
                    if "1080p" in episode:
                        epi = re.search(r"(^.*?)1080.*?-(.*?.mkv)", episode)
                    elif "2160p" in episode:
                        epi = re.search(r"(^.*?)(2160.*?)WEB.*?-(.*?.mkv)", episode)
                    elif "720p" in episode:
                        epi = re.search(r"(^.*?)(?:720p|720p\.10bit)(?:\.WEB-DL|\.WEBRip|\.).*?-(.*?.mkv)", episode)
                    # if epi is None:

                    first_part = epi.group(1)
                    second_part = epi.group(2)
                    if "[eztv.re]" in second_part:
                        second_part = "MeGusta.mkv"
                    elif "[EZTVx.to]" in second_part:
                        second_part = "MeGusta.mkv"
                    new_episode_name = first_part + second_part
                    logger.info("Waiting for 3 seconds...")
                elif "WEB" in episode or "BluRay" in episode:
                    epi = re.search(r"(^.*?)1080.*?(WEB|BluRay).*?-(.*?.mkv)", episode)
                    first_part = epi.group(1)
                    second_part = epi.group(2)
                    third_part = epi.group(3)
                    new_episode_name = first_part + second_part + "." + third_part

                # logger.debug(first_part)
                # logger.debug(second_part)
                # new_episode_name = first_part + second_part + third_part
                # logger.debug(new_episode_name)
                logger.info("Renaming episode to {}".format(new_episode_name))
                os.rename(join(self.src_dir, episode), join(self.src_dir, new_episode_name))
            except:
                logger.error("Could not change the name of the file")

    def full_process(self):
        self.extract_files()
        self.change_names()
        if self.src_dir != self.dst_dir:
            self.move_files()
        # log_dir = os.getcwd()
        # log_dir = join(log_dir, 'errors.log')
        # move(log_dir, join(self.dst_dir, 'errors.log'))

# DefaultSeries = Tvseries()


if __name__ == "__main__":
    logging.info("Starting cleaning process..")
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    rarfile.UNRAR_TOOL = cfg["rar_tool"]["path"]
    DefaultSeries = Tvseries()
    DefaultSeries.set_dirs(cfg["directories"]["extraction"]["source"], cfg["directories"]["extraction"]["destination"])
    DefaultSeries.full_process()