from os import path
import pickle
from datetime import datetime
from plexapi.server import PlexServer

def create_plex_server(server, token):
  return PlexServer(server, token = token)

def update_plex(library_id, directory, plex):
  # Get the library with the specified ID
  library = plex.library.sectionByID(library_id)
  # Perform a partial update of the library
  library.update(directory)

def plex_library(media_path, libraries):
  for library in libraries:
    if library["path"] in media_path:
      return library["id"]
  return None

def plex_path(media_path, plex_base, base_path):
  return media_path.replace(base_path, plex_base)

def get_plex_data(plex):
  movies_data = []
  collections_data = []
 
  try:
    with open("movies_data.pkl", "rb") as f:
      pkl_data = pickle.load(f)
      movies_data = pkl_data['data']
      last_updated = pkl_data['last_updated']
      last_updated_date = datetime.fromtimestamp(last_updated).strftime("%Y-%m-%d")
  except FileNotFoundError:
    last_updated_date = "2000-01-01"

  # Use the date in the search filter
  for library_id in range(13, 35):
    library = plex.library.sectionByID(library_id)
    for movie in library.search(filters={"addedAt>>": last_updated_date}):
      movie_data = {
          'title': movie.title,
          'path': path.dirname(movie.locations[0]),
          'addedAt': movie.addedAt
      }
      movies_data.append(movie_data)

    for collection in library.collections():
      collection_data = {
        'name': collection.title,
        'path': library.locations[0]
      }
      collections_data.append(collection_data)

    # Save the updated data to the cache files
    with open("movies_data.pkl", "wb") as f:
         pickle.dump({'data': movies_data, 'last_updated': datetime.now().timestamp()}, f)
         f.close()
    with open("collections_data.pkl", "wb") as f:
        pickle.dump(collections_data, f)
        f.close()

