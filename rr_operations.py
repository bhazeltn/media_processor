from pyarr import RadarrAPI
import requests

def remove_movie_from_radarr(movie_id, radarr_api_url, api_key):
    """
    Remove a movie from Radarr and add it to the exclusion list.

    Args:
    movie_id (int): The ID of the movie to be removed.
    api_key (str): The API key for accessing Radarr.
    radarr_api_url (str): The URL of the Radarr API endpoint.

    Returns:
    None
    """
    # Connect to Radarr API
    print("connecting to Radarr")
    radarr = RadarrAPI(radarr_api_url, api_key)
    print("connected to Radarr")
    # Set timeout for the API request
    timeout = 5 # in seconds
  
    # Remove movie from Radarr and add to exclusion list
    try:
        radarr.del_movie(movie_id, delete_files=False, add_exclusion=True)
    except requests.exceptions.Timeout as error:
        print(f"Request Timeout: The API endpoint did not respond within {timeout} seconds.")