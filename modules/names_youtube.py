import yt_dlp
import time
import os
import unicodedata

def get_video_titles(channel_url, delay=2):
     
    """Gets all video titles from a YouTube channel, with an optional small delay."""
    options = {
        'quiet': True,
        'extract_flat': 'in_playlist',
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        time.sleep(delay)  # Wait after extraction
        titles = [video['title'] for video in info.get('entries', [])]
        return sorted(titles)

def search_youtube(query, delay=1):
    """Searches YouTube for a query and returns the first video title found."""

    # Normalize query to remove accents (e.g., Pokémon -> Pokemon)
    query = ''.join(c for c in unicodedata.normalize('NFD', query) if unicodedata.category(c) != 'Mn')

    options = {
        'quiet': True,
        'extract_flat': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            time.sleep(delay)
            if 'entries' in info and info['entries']:
                return info['entries'][0]['title']
        except Exception as e:
            print(f"⚠️ Error searching YouTube: {e}")
    return None

def save_titles_to_file(titles, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(f"{title}\n" for title in titles)

def create_data(channel_url = 'https://www.youtube.com/@TheMisadventuresofSiskelEbert/videos',
                output_path='data/videos_youtube.txt'):
    titles = get_video_titles(channel_url)
    save_titles_to_file(titles, output_path)

if __name__ == '__main__':
    url = 'https://www.youtube.com/@TheMisadventuresofSiskelEbert/videos'
    create_data()
