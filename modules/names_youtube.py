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

def search_youtube(query, prefix=None, delay=1, validator=None):
    """
    Searches YouTube for a query.
    If 'prefix' is provided, it assumes 'query' is a slash-separated list of titles.
    It tries searching for the full list, and if not found, iteratively removes the last
    title, stopping at 2 titles. It also includes a fallback from "Siskel & Ebert" to "Ebert".
    """
    primary_queries = []
    secondary_queries = []  # Fallback for "Siskel & Ebert" -> "Ebert"    

    if prefix and '/' in query:
        parts = [p.strip() for p in query.split('/') if p.strip()]
        num_parts = len(parts)

        if num_parts > 1:
            # Strategy: Iteratively remove titles from the START of the query.
            # This handles cases where the beginning of the episode title is incorrect.
            # Starts at i=0 to include the full query. Stops when < 2 titles would remain.
            for i in range(0, num_parts - 1):
                sub_query_parts = parts[i:]
                if len(sub_query_parts) >= 2:
                    sub_query = " ".join(sub_query_parts)
                    primary_queries.append(f"{prefix} {sub_query}")
                    if prefix == "Siskel & Ebert":
                        secondary_queries.append(f"Ebert {sub_query}")
                
        else:  # Handle cases with only one title
            primary_queries.append(f"{prefix} {parts[0]}")
    else:
        # For non-slash queries, just create one search term
        primary_queries.append(f"{prefix} {query}" if prefix else query)
    
    all_queries = primary_queries + secondary_queries

    options = {
        'quiet': True,
        'extract_flat': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        for q in all_queries:
            q_norm = ''.join(c for c in unicodedata.normalize('NFD', q) if unicodedata.category(c) != 'Mn')
            try:
                info = ydl.extract_info(f"ytsearch1:{q_norm}", download=False)
                time.sleep(delay)
                if 'entries' in info and info['entries']:
                    title = info['entries'][0]['title']
                    if validator and not validator(title):
                        continue
                    # If valid, or no validator, return immediately.
                    return title
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
    create_data()
