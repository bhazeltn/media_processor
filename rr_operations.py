import pyarr

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
    radarr = pyarr.Radarr(radarr_api_url, api_key)

    # Remove movie from Radarr and add to exclusion list
    try:
        radarr.movie.remove(movie_id, add_import_exclusion=True, delete_files=False)
    except pyarr.exceptions.RadarrError as error:
        print(f"Error: {error}")