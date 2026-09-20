import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html import escape


# ============================================================
# CHAÎNES YOUTUBE
# ============================================================

CHANNELS = {
    "SPATULE BROS": "UCr85SbHVJydkcsXnt6kX2dg",
    "Monsieur Phi": "UCqA8H22FwgBVcF3GJpp0MQw",
    "Dany Caligula": "UCxJka_qnTVquoIL-PQV5POg",
    "Le Tropeur": "UCrpqKTyAxJWSpwmA_BfWTjw",
    "Durendal1": "UCcliHNE38fJ4n4gYYB0TCQw",
    "Regelegorila": "UCouHAi3jWpC8lAqsoeM_zOA",
    "France Culture": "UCd5DKToXYTKAQ6khzewww2g",
    "Science4All": "UC0NCbj8CxzeCGIF6sODJ-7A",
}


# ============================================================
# PARAMÈTRES
# ============================================================

DAYS = 7

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

NAMESPACE = {
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "atom": "http://www.w3.org/2005/Atom"
}

date_limite = datetime.now(timezone.utc) - timedelta(days=DAYS)


# ============================================================
# RÉCUPÉRATION DES VIDÉOS
# ============================================================

all_videos = []

for channel_name, channel_id in CHANNELS.items():

    rss_url = (
        "https://www.youtube.com/feeds/videos.xml"
        f"?channel_id={channel_id}"
    )

    try:
        response = requests.get(
            rss_url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            print(
                f"Erreur {response.status_code} : "
                f"{channel_name}"
            )
            continue

        root = ET.fromstring(response.text)

    except Exception as e:
        print(f"Erreur avec {channel_name} : {e}")
        continue

    for entry in root.findall("atom:entry", NAMESPACE):

        title_element = entry.find(
            "atom:title",
            NAMESPACE
        )

        published_element = entry.find(
            "atom:published",
            NAMESPACE
        )

        video_id_element = entry.find(
            "yt:videoId",
            NAMESPACE
        )

        if (
            title_element is None
            or published_element is None
            or video_id_element is None
        ):
            continue

        title = title_element.text
        published = published_element.text
        video_id = video_id_element.text

        date_video = datetime.fromisoformat(
            published.replace("Z", "+00:00")
        )

        # ----------------------------------------------------
        # FILTRE : 7 DERNIERS JOURS
        # ----------------------------------------------------

        if date_video < date_limite:
            continue

        # ----------------------------------------------------
        # FILTRE : 2 # OU PLUS
        # ----------------------------------------------------

        if title.count("#") >= 2:
            continue

        link = (
            "https://www.youtube.com/watch?v="
            + video_id
        )

        all_videos.append({
            "channel": channel_name,
            "title": title,
            "date": date_video,
            "link": link,
        })


# ============================================================
# TRI : PLUS RÉCENT EN PREMIER
# ============================================================

all_videos.sort(
    key=lambda video: video["date"],
    reverse=True
)


# ============================================================
# CRÉATION DES CARTES HTML
# ============================================================

cards = ""

for video in all_videos:

    date_formatted = video["date"].strftime(
        "%d/%m/%Y à %H:%M"
    )

    cards += f"""
    <article class="video-card">

        <div class="channel">
            📺 {escape(video["channel"])}
        </div>

        <h2>
            {escape(video["title"])}
        </h2>

        <div class="date">
            📅 {date_formatted}
        </div>

        <a
            class="watch"
            href="{escape(video["link"])}"
            target="_blank"
        >
            ▶️ Voir la vidéo
        </a>

    </article>
    """


# ============================================================
# SI AUCUNE VIDÉO
# ============================================================

if not all_videos:
    cards = """
    <div class="empty">
        Aucune nouvelle vidéo trouvée.
    </div>
    """


# ============================================================
# PAGE HTML
# ============================================================

html = f"""
<!DOCTYPE html>

<html lang="fr">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <meta
        name="theme-color"
        content="#111827"
    >

    <title>Mes vidéos YouTube</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            background: #f3f4f6;
            color: #111827;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }}

        header {{
            background: #111827;
            color: white;
            padding: 24px 16px;
            text-align: center;
        }}

        header h1 {{
            margin: 0 0 8px 0;
            font-size: 26px;
        }}

        header p {{
            margin: 0;
            opacity: 0.75;
            font-size: 14px;
        }}

        main {{
            max-width: 800px;
            margin: auto;
            padding: 16px;
        }}

        .video-card {{
            background: white;
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow:
                0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        .channel {{
            color: #6b7280;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        h2 {{
            font-size: 19px;
            line-height: 1.4;
            margin: 0 0 10px 0;
        }}

        .date {{
            color: #6b7280;
            font-size: 13px;
            margin-bottom: 15px;
        }}

        .watch {{
            display: block;
            background: #dc2626;
            color: white;
            text-decoration: none;
            text-align: center;
            padding: 12px;
            border-radius: 9px;
            font-weight: 600;
        }}

        .watch:active {{
            opacity: 0.8;
        }}

        .empty {{
            background: white;
            border-radius: 14px;
            padding: 30px;
            text-align: center;
            color: #6b7280;
        }}

        .count {{
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            margin: 8px 0 18px;
        }}

    </style>

</head>

<body>

<header>

    <h1>📺 Mes vidéos YouTube</h1>

    <p>
        Vidéos publiées durant les 7 derniers jours
    </p>

</header>

<main>

    <div class="count">
        {len(all_videos)} vidéo(s) trouvée(s)
    </div>

    {cards}

</main>

</body>

</html>
"""


# ============================================================
# ÉCRITURE DU FICHIER
# ============================================================

with open(
    "index.html",
    "w",
    encoding="utf-8"
) as file:

    file.write(html)


print(
    f"Page créée avec {len(all_videos)} vidéo(s)."
)
