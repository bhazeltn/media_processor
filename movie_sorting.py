import requests, pickle, shutil, traceback, os
import pandas as pd
from tmdbv3api import TMDb
from tmdbv3api import Movie

def get_movie_data(tmdb_id, imdb_id, tmdb_api, omdb_api):
    def _get_tmdb_data(tmdb_id, tmdb_api):
        tmdb = TMDb()
        tmdb.api_key = tmdb_api
        movie = Movie()
        tmdb_data = movie.details(tmdb_id)
        return tmdb_data

    def _get_omdb_data(imdb_id, omdb_api):
        if imdb_id is None:
            return {}
        omdb_data = requests.get(f"http://www.omdbapi.com/?apikey={omdb_api}&i={imdb_id}").json()
        return omdb_data

    tmdb_data = _get_tmdb_data(tmdb_id, tmdb_api)
    omdb_data = _get_omdb_data(imdb_id, omdb_api)

    missing_data = {}
    production_companies = [company['name'] for company in tmdb_data.production_companies]
    if not tmdb_data.production_companies:
        missing_data['production_companies'] = omdb_data.get('Production')
    if not tmdb_data.production_countries:
        missing_data['production_countries'] = omdb_data.get('Country')
    if not tmdb_data.spoken_languages:
        missing_data['spoken_languages'] = omdb_data.get('Language')
    genres = [genre['name'] for genre in tmdb_data.genres]
    if not tmdb_data.genres:
        missing_data['genres'] = omdb_data.get('Genre')

    try:
        title = tmdb_data.original_title
    except:
        title = tmdb_data.title

    data = {
        'collection': tmdb_data.belongs_to_collection.name if tmdb_data.belongs_to_collection else None,
        'production_companies': production_companies or missing_data.get('production_companies'),
        'production_countries': tmdb_data.production_countries or missing_data.get('production_countries'),
        'spoken_languages': tmdb_data.spoken_languages or missing_data.get('spoken_languages'),
        'genres': genres or missing_data.get('genres'),
        'movie_name': f"{title} ({tmdb_data.release_date[:4]})",
        'title': title
    }

    return data


def determine_movie_path(tmdb_data, base_path, plex_movie_path, current_path, isUHD):
  cur_path, file_name = path.split(current_path)

  def join_path(base_path, *args):
    if tmdb_data['collection']:
        return path.join(base_path, *args, tmdb_data['collection'] or '', tmdb_data['movie_name'], file_name)
    else:
        return path.join(base_path, *args, tmdb_data['movie_name'], file_name)
  
  genre = tmdb_data.get('genres', [])
  
  if not genre:
    print("No genre found")
    if isUHD:
      return join_path(base_path, 'uhd_unknown')
    else:
      return join_path(base_path, 'movie_unknown')
  
  
  with open("data/movies_data.pkl", "rb") as f:
    plex_movies_data = pickle.load(f)["data"]
  with open("data/collections_data.pkl", "rb") as f:
    plex_collections_data = pickle.load(f)
    plex_movies = pd.DataFrame(plex_movies_data)
    plex_collections = pd.DataFrame(plex_collections_data)

  production_company = tmdb_data.get('production_companies', '')
  production_country = tmdb_data.get('production_countries', '')
  language = tmdb_data.get('spoken_languages', '')
  
  production_company_set = set(production_company)
  allowed_companies = {'Marvel Studios', 'DC Films', 'DC Studios'}
  
  
  matching_collection = plex_collections.loc[plex_collections['name'] == tmdb_data['collection']]
  if not matching_collection.empty:
    collection_path = matching_collection['path'].iloc[0]
    return join_path(collection_path).replace(plex_movie_path, base_path)
  
  
  if tmdb_data['movie_title'] in plex_movies['title'].values:
    new_path =  plex_movies.loc[plex_movies['title'] == tmdb_data['movie_title'], 'path'].iloc[0]
    return new_path.replace(plex_movie_path, base_path)
  
  if allowed_companies.intersection(production_company_set):
    return join_path(base_path, 'Marvel and DC')
  
  if 'Philippines' in [x.get('name','') for x in production_country] or 'Tagalog' in [x.get('english_name','') for x in language]:
      return join_path(base_path, 'Filipino')
  
  if genre[0] == "TV Movie":
    if len(genre) > 1 and genre[1] != 'TV Movie':
      return join_path(base_path, genre[1])
    else:
      return join_path(base_path, 'TV Movie')
  elif 'Horror' in genre:
      return join_path(base_path, 'Horror')
  elif 'Animation' in genre:
      return join_path(base_path, 'Animated')
  elif 'Science Fiction' in genre: 
      return join_path(base_path, 'SciFi')
  elif 'Comedy' in genre and 'Romance' in genre:
      return join_path(base_path, 'RomCom')
  else:
      return join_path(base_path, genre[0])
  
def move_movie(source_path, destination_path):
  """Move a file from source_path to destination_path, creating the destination directory if it doesn't exist.

  Args:
  source_path (str): The path of the file to be moved, including the file name.
  destination_path (str): The path where the file will be moved to, including the file name. The directory part of the path will be created if it doesn't exist.

  Returns:
  None
  """
  try:
    # Ensure the destination directory exists
    print(f"Making directory: {os.path.dirname(destination_path)}")
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    print(f"Directory made: {os.path.dirname(destination_path)}")
  except FileNotFoundError as e:
    print(f"Error: The parent directory of {destination_path} does not exist")
  except PermissionError as e:
    print(f"Error: You do not have permission to create the directory {os.path.dirname(destination_path)}")
  except Exception as e:
    print(f"Error: An unexpected error occurred while creating the directory: {e}")
    return
  try:
    # Move the file to the destination directory
    print(f"Moving file {source_path} to {destination_path}")
    r = shutil.move(source_path, destination_path)
    print(r)
    print(f"File moved: {source_path}")
  except FileNotFoundError as e:
    print(f"Error: The file {source_path} does not exist")
  except PermissionError as e:
    print(f"Error: You do not have permission to move the file {source_path}")
  except Exception as e:
    print(f"Error: An unexpected error occurred while moving the file: {e}")
    print("Stack trace:")
    traceback.printexc()

def movie_directory(isUHD, uhd_dir, movie_dir):
  """
  Returns the partial path that the movies will be stored in
  
  Parameters:
  isUHD (bool): Determines if the movie is UHD (True) or not (False)
  uhd_dir (str): Directory for UHD movies
  movie_dir (str): Directory for all other movies

  Returns:
  str: The directory to store the movie in
  """
  return uhd_dir if isUHD else movie_dir