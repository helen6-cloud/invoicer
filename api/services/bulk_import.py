from api.models import Titles
from .omdb import fetch_from_omdb


def bulk_update_titles_from_omdb():
    titles = Titles.objects.all()
    updated = 0

    for title in titles:
        data = fetch_from_omdb(title.title_name)
        if not data:
            continue

        title.ozet = data.get("Plot") or title.ozet
        title.poster_url = data.get("Poster") or title.poster_url
        title.cesit = data.get("Type") or title.cesit

        year = data.get("Year")
        if year and year[:4].isdigit():
            title.yil = int(year[:4])

        runtime = data.get("Runtime")
        if runtime and "min" in runtime:
            title.sure = int(runtime.replace(" min", ""))

        title.save()
        updated += 1

    return updated
