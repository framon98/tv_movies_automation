import logging
import coloredlogs
import os
from os import listdir
import json
from os.path import join
import re
import yaml
from datetime import datetime
import subprocess

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

#Config info



class List_Creator:
    def __init__(self):
        self.src_dir = ""
        self.dst_dir = ""
        self.series = []
        self.movies = []

    def set_dirs(self, src, dst="", same_dir=False):
        logger.debug("Setting directories for source and destination")
        self.src_dir = os.path.normpath(src)
        logger.debug("Source directory is: {}".format(self.src_dir))
        if same_dir:
            self.dst_dir = self.src_dir
        else:
            self.dst_dir = os.path.normpath(dst)
        logger.debug("Destination directory is: {}".format(self.dst_dir))

    def filename_reader(self):
        current_time = datetime.now()
        with open("new_content.txt", "w") as list_file:
            list_file.write(str(current_time) + "\n")
        logger.debug("Reading directory to get all file names in a list")
        for file in listdir(self.src_dir):
            if os.path.isdir(join(self.src_dir, file)):
                # logger.warning("{} is a directory and cannot be renamed".format(file))
                continue
            elif ".mkv" in os.path.splitext(file):
                if re.search(r"(S\d\dE\d\d)", file) is not None:
                    self.series.append(file)
                elif re.search(r"(20\d\d)", file) is not None or re.search(r"(19\d\d)", file) is not None:
                    self.movies.append(file)
                # if "(" in file or ")" in file:
                #     # logger.debug("Appending a movie")
                #     self.movies.append(file)
                # else:
                #     # logger.debug("Appending a tv show")
                #     self.series.append(file)
        logger.debug("These are movies")
        print(self.movies)
        logger.debug("These are tv shows")
        print(self.series)
                # print(file)

    def list_movies(self):
        logger.debug("These are the Movies to save")
        print(self.movies)
        for movie in self.movies:
            if "(" in movie:
                movie_name = movie.partition("(")[0]
                movie_year = re.search(r"\(.*?\)", movie)
                movie_name += f"{movie_year.group()} "
                if "BDRip" in movie or "BDrip" in movie:
                    movie_name += "[BluRay] Audio Dual Latino-Ingles"
                elif "Dual" in movie:
                    movie_name += "[Digital] Audio Dual Latino-Ingles"
                else:
                    movie_name += "[Digital] Audio Ingles"
                # print(movie_name)
                with open("new_content.txt", "a") as list_file:
                    list_file.write(movie_name + "\n")
            else:
                movie_name_year = re.search(r"(^.*)(20\d\d|19\d\d)", movie)
                # logger.debug("whole search %s",movie_name_year)
                movie_name = movie_name_year[1].replace(".", " ")
                # logger.debug("movie name: %s", movie_name)
                movie_year = movie_name_year[2]
                # logger.debug("Movie year: %s", movie_year)
                movie_name += f"({movie_year}) "
                if "WEB" in movie or "BluRay" in movie:
                    if "BluRay" in movie:
                        movie_name += "[BluRay] Audio Ingles"
                    elif "Dual" in movie:
                        movie_name += "[Digital] Audio Dual Latino-Ingles"
                    else:
                        movie_name += "[Digital] Audio Ingles"
                with open("new_content.txt", "a") as list_file:
                    list_file.write(movie_name + "\n")

    def read_reference(self, filename):
        with open(filename) as json_ref:
            shows_ref = json.load(json_ref)
        return shows_ref

    def list_shows(self):
        logger.debug("These are the TV Shows to save")
        # shows_set = set()
        ref_dict = self.read_reference("shows_ref.json")["Series"]
        # print(ref_dict)

        for show in self.series:
            episode_separation = re.search(r"(^.*?).(S\d*E\d*).", show)
            episode_title = episode_separation.group(1).replace(".", " ")
            episode_title = ''.join((idxi for idxi in episode_title if not idxi.isdigit())).strip()

            episode_full_filename = f"{episode_title} [{ref_dict[episode_title]}] {episode_separation.group(2)}"

            with open("new_content.txt", "a") as list_file:
                list_file.write(episode_full_filename + "\n")
            # print(episode_full_filename)
            # shows_set.add(episode_title)
        # for serie in shows_set:
        #     print(serie)
        # print(shows_set)

    def open_file(self):
        subprocess.Popen(["notepad", "new_content.txt"])


if __name__ == "__main__":
    logging.debug("Running...")
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    SeriesList = List_Creator()
    SeriesList.set_dirs(cfg["directories"]["source"], cfg["directories"]["destination"])
    SeriesList.filename_reader()
    SeriesList.list_movies()
    SeriesList.list_shows()
    SeriesList.open_file()
