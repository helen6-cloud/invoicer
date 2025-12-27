from backend.api import Titles
from .omdb import fetch_title_from_omdb


def import_title_from_omdb(title_name):
    data = fetch_title_from_omdb(title_name)

    if not data:
        return None, "OMDb'de bulunamadı"

    title, created = Titles.objects.get_or_create(
        title_name=data["title"],
        defaults={
            "yil": data["year"] or 0,
            "ozet": data["plot"],
            "sure": int(data["runtime"].replace(" min", "")) if data["runtime"] and "min" in data["runtime"] else None,
            "poster_url": data["poster_url"],
            "cesit": data["type"],
        }
    )

    return title, created
