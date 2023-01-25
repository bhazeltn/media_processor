import requests

def remove_movie_from_radarr(movie_id, radarr_api_key, radarr_api_url):
  # Remove the movie from Radarr
  requests.delete(f"{radarr_api_url}/api/movie/{movie_id}?apikey={radarr_api_key}")

  # Add the movie to the exclusion list
  data = {
      "tmdbId": movie_id,
      "qualityProfileId": 1,
      "title": "",
      "titleSlug": "",
      "rootFolderPath": "",
      "sizeOnDisk": 0
  }
  requests.post(f"{radarr_api_url}/api/exclusion?apikey={radarr_api_key}", json=data)
