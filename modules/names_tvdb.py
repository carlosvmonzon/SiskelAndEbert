import requests, re
from bs4 import BeautifulSoup
from modules.names_youtube import save_titles_to_file

def get_tvdb_episodes(url, min_i, max_i):

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract episode titles, removing the season/episode reference (like S01E01)
    episodes = []
    dates = []

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

            # The air date is the first <li> in the "list-inline text-muted" row
            # (e.g. <li>September 20, 1986</li><li>Syndication</li>)
            date_text = "N/A"
            date_ul = episode_li.find("ul", class_="list-inline text-muted")
            if date_ul:
                date_li = date_ul.find("li")
                if date_li and date_li.get_text(strip=True):
                    date_text = date_li.get_text(strip=True)
            # Never write a blank line: open_files() strips blank lines, which
            # would desync this file's line numbers against the episodes file.
            dates.append(date_text)

    return episodes, dates

def create_data(url_snippet="siskel-and-ebert-at-the-movies", output_path="data/tvdb_episodes.txt",
                min_i=1, max_i=591):
    # Get episode titles and air dates from TVDB
    url = f"https://thetvdb.com/series/{url_snippet}/allseasons/official"
    tvdb_episodes, tvdb_dates = get_tvdb_episodes(url, min_i=min_i, max_i=max_i)
    save_titles_to_file(tvdb_episodes, output_path)

    # Air dates are written to a parallel file (same order as output_path), so the
    # Rumble-matching fallback can look an episode up by its exact air date.
    dates_path = re.sub(r"\.txt$", "_dates.txt", output_path)
    save_titles_to_file(tvdb_dates, dates_path)
