import requests
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

# ─── AUTH ───────────────────────────────────────────

def get_access_token():
    print("Getting Twitch access token...")
    response = requests.post(
        'https://id.twitch.tv/oauth2/token',
        params={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
    )
    token = response.json().get('access_token')
    if token:
        print("Access token retrieved")
    else:
        print("Failed to get access token")
        print(response.json())
    return token

# ─── TWITCH ─────────────────────────────────────────

def get_top_games(limit=100):
    print(f"\nFetching top {limit} games from Twitch...")
    token = get_access_token()
    response = requests.get(
        'https://api.twitch.tv/helix/games/top',
        headers={
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {token}'
        },
        params={'first': limit}
    )
    games = response.json().get('data', [])
    print(f"Retrieved {len(games)} games from Twitch")

    # filter out non-games — they have no igdb_id
    games_only = [g for g in games if g.get('igdb_id')]
    print(f"{len(games_only)} are actual games (filtered out non-game categories)")

    print("\nTop 10 games on Twitch right now:")
    for i, game in enumerate(games_only[:10], 1):
        print(f"  {i}. {game['name']} (IGDB ID: {game['igdb_id']})")

    return games_only

# ─── IGDB ────────────────────────────────────────────

def get_igdb_genre(igdb_id: str, token: str):
    response = requests.post(
        'https://api.igdb.com/v4/games',
        headers={
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {token}'
        },
        data=f'where id = {igdb_id}; fields name,genres.name; limit 1;'
    )
    try:
        results = response.json()
        if isinstance(results, list) and len(results) > 0 and 'genres' in results[0]:
            return results[0]['genres'][0]['name']
    except Exception as e:
        print(f"  IGDB error for ID {igdb_id}: {e}")
    return None

# ─── IGDB TO KAGGLE GENRE MAP ────────────────────────

IGDB_TO_KAGGLE = {
    'Role-playing (RPG)':   'Role-Playing',
    'Shooter':              'Shooter',
    'Sport':                'Sports',
    'Racing':               'Racing',
    'Fighting':             'Fighting',
    'Simulator':            'Simulation',
    'Puzzle':               'Puzzle',
    'Platform':             'Platform',
    'Strategy':             'Strategy',
    'Adventure':            'Adventure',
    'Arcade':               'Action',
    'Hack and slash/Beat em up': 'Action',
    'Real Time Strategy (RTS)': 'Strategy',
    'Point-and-click':  'Adventure',
    'Card & Board Game': 'Misc',
    'Tactical':         'Shooter',
    'Indie':                'Misc',
    'Music':                'Misc',
}

# ─── MAIN FUNCTION ───────────────────────────────────

def get_genre_viewership():
    print("="*40)
    print("Starting Twitch + IGDB genre viewership fetch")
    print("="*40)

    top_games = get_top_games(100)
    token = get_access_token()

    genre_viewers = {}
    genre_titles = {}
    skipped = 0

    print(f"\nMapping {len(top_games)} games to Kaggle genres via IGDB...")

    for game in top_games:
        name = game['name']
        igdb_id = game['igdb_id']

        igdb_genre = get_igdb_genre(igdb_id, token)
        if not igdb_genre:
            print(f"  No genre found for: {name}")
            skipped += 1
            continue

        kaggle_genre = IGDB_TO_KAGGLE.get(igdb_genre)
        if not kaggle_genre:
            print(f"  Unmapped IGDB genre '{igdb_genre}' for: {name}")
            skipped += 1
            continue

        if kaggle_genre not in genre_viewers:
            genre_viewers[kaggle_genre] = 0
            genre_titles[kaggle_genre] = []

        genre_viewers[kaggle_genre] += 1
        genre_titles[kaggle_genre].append(name)
        print(f"  {name} → {igdb_genre} → {kaggle_genre}")

    print(f"\n{'='*40}")
    print(f"RESULTS")
    print(f"{'='*40}")
    print(f"Games mapped:  {len(top_games) - skipped}")
    print(f"Games skipped: {skipped}")
    print(f"\nGenre viewership (titles in Twitch top 100):")
    for genre, count in sorted(genre_viewers.items(), key=lambda x: x[1], reverse=True):
        titles = ', '.join(genre_titles[genre][:3])
        print(f"  {genre}: {count} titles — e.g. {titles}")

    return genre_viewers, genre_titles

if __name__ == "__main__":
    get_genre_viewership()