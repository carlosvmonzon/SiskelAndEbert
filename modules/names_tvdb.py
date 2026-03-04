import requests, re
import os
from bs4 import BeautifulSoup
                
def get_tvdb_episodes(url, min_i, max_i):
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract episode titles, removing the season/episode reference (like S01E01)
    episodes = []
    
    # Here we extract all <a> tags within <li> with classes containing episode titles
    for i, episode_li in enumerate(soup.find_all("li", class_="list-group-item"), start=1):
        if max_i and i > max_i:
            continue
        if i < min_i:
            continue
        title_tag = episode_li.find("a")
        if title_tag:
            full_title = title_tag.get_text(strip=True)  # Full title with season/episode reference
            clean_title = re.sub(r'S\d{2}E\d{2}', '', full_title).strip()  # Remove reference like S01E01
            episodes.append(str(i) + ' ' + clean_title)
       

    return episodes

def create_data(url_snippet="siskel-and-ebert-at-the-movies", output_path="data/tvdb_episodes.txt",
                min_i=1, max_i=591):
    # Get episode titles from TVDB
    url = f"https://thetvdb.com/series/{url_snippet}/allseasons/official"
    tvdb_episodes = get_tvdb_episodes(url, min_i=min_i, max_i=max_i)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for video in tvdb_episodes:
            f.write(video + "\n")
