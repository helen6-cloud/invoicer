import requests
from django.conf import settings


OMDB_BASE_URL = "https://www.omdbapi.com/"


def fetch_from_omdb(title_name):
    api_key = getattr(settings, "OMDB_API_KEY", None)

    if not api_key:
        raise ValueError("HATA: settings.py dosyasında OMDB_API_KEY tanımlı değil!")
    params = {
        "t": title_name,
        "apikey": settings.OMDB_API_KEY,
        "plot": "full"
    }

    response = requests.get(OMDB_BASE_URL, params=params, timeout=10)
    data = response.json()

    if data.get("Response") == "False":
        return None

    return {
        "title": data.get("Title"),
        "year": int(data["Year"][:4]) if data.get("Year") else None,
        "plot": data.get("Plot"),
        "runtime": data.get("Runtime"),
        "poster_url": data.get("Poster"),
        "imdb_id": data.get("imdbID"),
        "type": data.get("Type"),
        "genre": data.get("Genre"),
        "imdb_rating": data.get("imdbRating"),
    }
def search_omdb(query, content_type=None):
    params = {
        "apikey": settings.OMDB_API_KEY,
        "s": query
    }

    if content_type:
        params["type"] = content_type  # movie | series

    response = requests.get("https://www.omdbapi.com/", params=params)
    data = response.json()

    if data.get("Response") == "False":
        return []

    return data.get("Search", [])
def get_omdb_detail(imdb_id):
    params = {
        "apikey": settings.OMDB_API_KEY,
        "i": imdb_id,

        "plot": "full"
    }

    response = requests.get("https://www.omdbapi.com/", params=params)
    return response.json()