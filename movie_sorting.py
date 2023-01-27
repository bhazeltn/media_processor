import requests, pickle, shutil
import pandas as pd
from tmdbv3api import TMDb
from tmdbv3api import Movie
from os import path

def get_movie_data(tmdb_id, imdb_id, tmdb_api, omdb_api):
  tmdb = TMDb()
  tmdb.api_key = tmdb_api
  movie = Movie()
  tmdb_data = movie.details(tmdb_id)
  missing_data = {}
  production_companies = [company['name'] for company in tmdb_data.production_companies]
  if not tmdb_data.production_companies:
    missing_data['production_companies'] = None
  if not tmdb_data.production_countries:
    missing_data['production_countries'] = None
  if not tmdb_data.spoken_languages:
    missing_data['spoken_languages'] = None
  genres = [genre['name'] for genre in tmdb_data.genres]
  if not tmdb_data.genres:
    missing_data['genres'] = None
    
  try:
    title = tmdb_data.original_title
  except:
    title = tmdb_data.title

  if missing_data:
    omdb_data = requests.get(f"http://www.omdbapi.com/?apikey={omdb_api}&i={imdb_id}").json()
    if 'Production' in omdb_data:
      if omdb_data['Production'] != 'N/A':
        missing_data['production_companies'] = omdb_data["Production"].split(',')
    if 'Country' in omdb_data:
      missing_data['production_countries'] = omdb_data['Country'].split(',')
    if 'Language' in omdb_data:
      missing_data['spoken_languages'] = omdb_data['Language'].split(',')
    if 'Genre' in omdb_data:
      missing_data['genres'] = omdb_data['Genre'].split(',')
   
  #Create a dictionary to store the values of the fields you want to return
  data = {
        'collection': tmdb_data.belongs_to_collection.name if tmdb_data.belongs_to_collection else None,
        'production_companies': production_companies,
        'production_countries': tmdb_data.production_countries or missing_data.get('production_countries'),
        'spoken_languages': tmdb_data.spoken_languages or missing_data.get('spoken_languages'),
        'genres': genres,
        'movie_name': f"{title} ({tmdb_data.release_date[:4]})",
        'title': title
        
    }
  return data

def determine_movie_path(tmdb_data, base_path, plex_movie_path):
  
  with open("data/movies_data.pkl", "rb") as f:
    plex_movies_data = pickle.load(f)["data"]
  with open("data/collections_data.pkl", "rb") as f:
    plex_collections_data = pickle.load(f)
    plex_movies = pd.DataFrame(plex_movies_data)
    plex_collections = pd.DataFrame(plex_collections_data)

  def join_path(base_path, *args):
    if tmdb_data['collection']:
        return path.join(base_path, *args, tmdb_data['collection'] or '', tmdb_data['movie_name'])
    else:
        return path.join(base_path, *args, tmdb_data['movie_name'])
  
  production_company = tmdb_data.get('production_companies', '')
  production_country = tmdb_data.get('production_countries', '')
  language = tmdb_data.get('spoken_languages', '')
  genre = tmdb_data.get('genres', '')
  
  production_company_set = set(production_company)
  allowed_companies = {'Marvel Studios', 'DC Films', 'DC Studios'}
  
  
  matching_collection = plex_collections.loc[plex_collections['name'] == tmdb_data['collection']]
  if not matching_collection.empty:
    collection_path = matching_collection['path'].iloc[0]
    return join_path(collection_path).replace(plex_movie_path, base_path)
  
  
  if tmdb_data['title'] in plex_movies['title'].values:
    new_path =  plex_movies.loc[plex_movies['title'] == tmdb_data['title'], 'path'].iloc[0]
    return new_path.replace(plex_movie_path, base_path)
  
  if allowed_companies.intersection(production_company_set):
    return join_path(base_path, 'Marvel and DC')
  elif 'Philippines' in [x.get('name','') for x in production_country] or 'Tagalog' in [x.get('english_name','') for x in language]:
      return join_path(base_path, 'Filipino')
  elif 'Horror' in genre:
      return join_path(base_path, 'Horror')
  elif 'Animation' in genre:
      return join_path(base_path, 'Animated')
  elif 'Science Fiction' in genre: 
      return join_path(base_path, 'SciFi')
  elif 'Comedy' in genre and 'Romance' in genre:
      return join_path(base_path, 'RomCom')
  elif genre:
      return join_path(base_path, genre[0])
  else:
      return join_path(base_path, 'unknown')
    
def move_movie(file_path, dest_path):
  shutil.move(file_path, dest_path)