import requests, pickle, shutil
import pandas as pd
from tmdbv3api import TMDb
from tmdbv3api import Movie
from os import path

def get_movie_data(tmdb_id: str, imdb_id: str, tmdb_api: str, omdb_api: str) -> Dict:
  """
  This function retrieves information about a movie including its title, release year, collection, production countries, 
  production companies, spoken languages, and genres.
  
  Parameters:
  tmdb_id (str): The TMDb movie id
  imdb_id (str): The IMDb movie id
  tmdb_api (str): The TMDb API key
  omdb_api (str): The OMDb API key
  
  Returns:
  Dict: A dictionary containing the movie data
  """
  def _get_missing_data_from_omdb(imdb_id, omdb_api):
    """
    Get missing movie data from OMDb

    Arguments:
        imdb_id {str} -- IMDb identifier
        omdb_api {str} -- API key for OMDb

    Returns:
        dict -- missing movie data in the form of a dictionary
    """
    omdb_data = requests.get(f"http://www.omdbapi.com/?apikey={omdb_api}&i={imdb_id}").json()
    missing_data = {}

    if 'Production' in omdb_data and omdb_data['Production'] != 'N/A':
      missing_data['production_companies'] = omdb_data["Production"].split(',')
    if 'Country' in omdb_data:
      missing_data['production_countries'] = omdb_data['Country'].split(',')
    if 'Language' in omdb_data:
      missing_data['spoken_languages'] = omdb_data['Language'].split(',')
    if 'Genre' in omdb_data:
      missing_data['genres'] = omdb_data['Genre'].split(',')

    return missing_data

def _get_tmdb_data(tmdb_id, tmdb_api):
  """
  Queries TMDb API for movie information
  
  Parameters:
  tmdb_id (str): The TMDb movie id
  tmdb_api (str): TMDb API Key

  Returns:
  dict: TMDb movie information in the following format:
    {
      "collection": str,
      "production_companies": List[str],
      "production_countries": List[str],
      "spoken_languages": List[str],
      "genres": List[str],
      "movie_name": str,
      "title": str
    }
  """
  tmdb = TMDb()
  tmdb.api_key = tmdb_api
  movie = Movie()
  tmdb_data = movie.details(tmdb_id)
  production_companies = [company['name'] for company in tmdb_data.production_companies]
  genres = [genre['name'] for genre in tmdb_data.genres]
  try:
    title = tmdb_data.original_title
  except:
    title = tmdb_data.title
  return {
    'collection': tmdb_data.belongs_to_collection.name if tmdb_data.belongs_to_collection else None,
    'production_companies': production_companies,
    'production_countries': tmdb_data.production_countries,
    'spoken_languages': tmdb_data.spoken_languages,
    'genres': genres,
    'movie_name': f"{title} ({tmdb_data.release_date[:4]})",
    'title': title,
  }



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