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
    # Define endpoint, header, and timeout
    endpoint = f"{radarr_api_url}/api/movie/{movie_id}"
    header = {'X-api-key': api_key}
    timeout = 5  # in seconds

    # Delete movie from Radarr and add to exclusion list
    params = {'addImportExclusion': True, 'deleteFiles': False}
    try:
        response = requests.delete(endpoint, headers=header, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        if response.status_code == 400:
            print("Bad Request: The request was invalid.")
        elif response.status_code == 401:
            print("Unauthorized: The API key is invalid.")
        elif response.status_code == 404:
            print("Not Found: The movie was not found in Radarr.")
        else:
            print(f"HTTP Error: {error}")
    except requests.exceptions.Timeout as error:
        print(f"Request Timeout: The API endpoint did not respond within {timeout} seconds.")
    except requests.exceptions.RequestException as error:
        print(f"Request Error: {error}")