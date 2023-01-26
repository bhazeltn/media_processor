#!/usr/bin/env python3

import yaml, threading, os, json
from concurrent.futures import ThreadPoolExecutor
from datetime import time, date

#Now imports from this project
from media_converting import convert
from media_uploader import upload_to_rclone
from movie_sorting import get_movie_data, determine_movie_path
from plex_operations import update_plex, plex_library, create_plex_server, plex_path, get_plex_data
from rr_operations import remove_movie_from_radarr

#Load and assign the starting variables
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

remotes = config["remotes"]
plex_server = config["plex_server"]
plex_token = config["plex_token"]
uhd_radarr_data = config["uhd_radarr_data"]
radarr_data = config["radarr_data"]
sonarr_data = config["sonarr_data"]
rclone_log_file =  config["rclone_log_file"] + str(date.today()) + ".log"
radarr_url = config["radarr_url"]
uhd_radarr_url = config["uhd_radarr_url"]
radarr_api = config["radarr_api"]
uhd_radarr_api = config["uhd_radarr_api"]
sickbeard_path = config["sickbeard_path"]
python_path = config["python_path"]
rclone_state_file = config["rclone_state"]
rclone_path = config["rclone_path"]
tmdb_api = config["tmdb_api"]
omdb_api = config["omdb_api"]
plex_movie_dest_path = config["plex_movie_destination_path"]
uhd_base_path = config["uhd_base_path"] 
movie_base_path = config["movie_base_path"]
base_path = config["base_path"]
threads = int(config["threads"])
libraries = config["libraries"]
plex_base_path = config["plex_base_path"]

rclone_state_lock = threading.Lock()

def tv_process(tv_json):
  full_path = os.path.join(base_path, tv_json["epidodepath"][1:])
  converted_path = convert(full_path, sickbeard_path, python_path)
  upload_to_rclone(converted_path, remotes, base_path, rclone_state_file, rclone_path, rclone_state_lock)
  plex_media_path = plex_path(converted_path, plex_base_path, base_path)
  library_id = plex_library(plex_media_path, libraries)
  update_plex(library_id, plex_media_path, create_plex_server(plex_server, plex_token))
  
def movie_process(movie_json, isUHD):
  plex = create_plex_server(plex_server, plex_token)
  #if isUHD:
  #  remove_movie_from_radarr(movie_json["movieid"], uhd_radarr_url, uhd_radarr_api)
  #else:
  #  remove_movie_from_radarr(movie_json["movieid"], radarr_url, radarr_api)
  #full_path = os.path.join(base_path, movie_json["moviepath"][1:])
  #converted_path = convert(full_path, sickbeard_path, python_path)
  print(os.getcwd())
  print("Hellllllo")
  plex_data = get_plex_data(plex)
  movie_data = get_movie_data(movie_json["tmdbid"], movie_json["imdbid"], tmdb_api, omdb_api)
  print(movie_data)

def main():
  with ThreadPoolExecutor(max_workers=threads) as executor:
    while True:
      if os.path.exists(sonarr_data):
        with open(sonarr_data) as f:
          data = json.load(f)
          executor.submit(tv_process, data)
        #os.remove(sonarr_data)
      elif os.path.exists(radarr_data):
        with open(radarr_data) as f:
          data = json.load(f)
          executor.submit(movie_process, data, False)
        #os.remove(radarr_data)
      elif os.path.exists(uhd_radarr_data):
          with open(uhd_radarr_data) as f:
            data = json.load(f)
            executor.submit(movie_process, data, True)
          #os.remove(uhd_radarr_data)
      else:
          sleep(1)

main()