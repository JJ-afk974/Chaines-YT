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

date_limite = (
    datetime.now(timezone.utc)
    - timedelta(days=DAYS)
)


# ============================================================
# RÉCUPÉRATION DES VIDÉOS
# ============================================================

videos_by_channel = {}

for channel_name, channel_id in CHANNELS.items():

    videos_by_channel[channel_name] = []

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
                f"❌ {channel_name} : "
                f"HTTP {response.status_code}"
            )
            continue

        root = ET.fromstring(response.text)

    except Exception as e:
        print(
            f"❌ Erreur avec {channel_name} : {e}"
        )
        continue


    # ========================================================
    # PARCOURS DES VIDÉOS
    # ========================================================

    for entry in root.findall(
        "atom:entry",
        NAMESPACE
    ):

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

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # AJOUT DE LA VIDÉO
        # ----------------------------------------------------

        videos_by_channel[channel_name].append({
            "title": title,
            "date": date_video,
            "link": (
                "https://www.youtube.com/watch?v="
                + video_id
            )
        })


# ============================================================
# TRI DES VIDÉOS
# ============================================================

for channel_name in videos_by_channel:

    videos_by_channel[channel_name].sort(
        key=lambda video: video["date"],
        reverse=True
    )


# ============================================================
# CONSTRUCTION DES CHAÎNES
# ============================================================

channels_html = ""
total_videos = 0

for channel_name, videos in videos_by_channel.items():

    # Ne pas afficher les chaînes sans vidéo
    if not videos:
        continue

    total_videos += len(videos)

    videos_html = ""

    for video in videos:

        date_formatted = video["date"].strftime(
            "%d/%m/%Y à %H:%M"
        )

        videos_html += (
            '<div class="video">'
            f'<div class="video-title">'
            f'{escape(video["title"])}'
            '</div>'
            f'<div class="video-date">'
            f'📅 {date_formatted}'
            '</div>'
            f'<a class="youtube-button" '
            f'href="{escape(video["link"])}" '
            f'target="_blank" '
            f'rel="noopener noreferrer">'
            '▶️ Voir sur YouTube'
            '</a>'
            '</div>'
        )

    nombre = len(videos)

    mot_video = "vidéo" if nombre == 1 else "vidéos"

    channels_html += (
        '<details class="channel">'
        '<summary>'
        f'<span class="channel-name">📺 '
        f'{escape(channel_name)}</span>'
        f'<span class="video-count">'
        f'{nombre} {mot_video}</span>'
        '</summary>'
        '<div class="videos">'
        f'{videos_html}'
        '</div>'
        '</details>'
    )


# ============================================================
# AUCUNE VIDÉO
# ============================================================

if not channels_html:

    channels_html = (
        '<div class="empty">'
        'Aucune vidéo trouvée durant les 7 derniers jours.'
        '</div>'
    )


# ============================================================
# TEXTE DU COMPTEUR
# ============================================================

mot_videos = "vidéo" if total_videos == 1 else "vidéos"


# ============================================================
# PAGE HTML
# ============================================================

html = f"""<!DOCTYPE html>
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
            padding: 25px 18px;
            text-align: center;
        }}

        header h1 {{
            margin: 0 0 7px 0;
            font-size: 25px;
        }}

        header p {{
            margin: 0;
            font-size: 14px;
            opacity: 0.7;
        }}

        main {{
            max-width: 800px;
            margin: auto;
            padding: 15px;
        }}

        .summary {{
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 15px;
        }}

        .channel {{
            background: white;
            border-radius: 13px;
            margin-bottom: 10px;
            overflow: hidden;
            box-shadow:
                0 2px 7px rgba(0, 0, 0, 0.08);
        }}

        .channel summary {{
            cursor: pointer;
            list-style: none;
            padding: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            font-weight: 600;
            user-select: none;
        }}

        .channel summary::-webkit-details-marker {{
            display: none;
        }}

        .channel summary::after {{
            content: "›";
            font-size: 25px;
            color: #9ca3af;
            transition: transform 0.2s;
        }}

        .channel[open] summary::after {{
            transform: rotate(90deg);
        }}

        .channel-name {{
            font-size: 17px;
        }}

        .video-count {{
            color: #6b7280;
            font-size: 14px;
            white-space: nowrap;
        }}

        .videos {{
            border-top: 1px solid #e5e7eb;
        }}

        .video {{
            padding: 17px;
            border-bottom: 1px solid #e5e7eb;
        }}

        .video:last-child {{
            border-bottom: none;
        }}

        .video-title {{
            font-size: 16px;
            line-height: 1.45;
            font-weight: 600;
            margin-bottom: 7px;
        }}

        .video-date {{
            color: #6b7280;
            font-size: 13px;
            margin-bottom: 12px;
        }}

        .youtube-button {{
            display: block;
            background: #dc2626;
            color: white;
            text-decoration: none;
            text-align: center;
            padding: 11px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
        }}

        .youtube-button:active {{
            opacity: 0.8;
        }}

        .empty {{
            background: white;
            border-radius: 13px;
            padding: 30px;
            text-align: center;
            color: #6b7280;
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

    <div class="summary">
        {total_videos} {mot_videos} trouvée(s)
    </div>

    {channels_html}

</main>

</body>

</html>
"""


# ============================================================
# CRÉATION DE INDEX.HTML
# ============================================================

with open(
    "index.html",
    "w",
    encoding="utf-8"
) as file:

    file.write(html)


print(
    f"✅ Page créée avec "
    f"{total_videos} vidéo(s)"
)
