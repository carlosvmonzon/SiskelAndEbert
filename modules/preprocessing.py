import re
from Levenshtein import ratio

def open_files(*file_paths):
    names_text = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                names_text.append([line.strip() for line in file if line.strip()])
        except FileNotFoundError:
            print(f"File not found: {file_path}. Creating '{file_path}'...")
    return names_text

def clean_title(title, header=False, roeper=False):
    """
    Cleans and splits a raw episode title string into a list of individual movie titles.
    
    Args:
        title (str): The raw title string.
        header (bool): If True, performs additional cleaning for YouTube-style headers.
        roeper (bool): If True, removes "Ebert & Roeper (YEAR)" branding.
                       If False, removes "Siskel & Ebert (YEAR)" branding.

    Returns:
        list: A list of cleaned movie title strings.
    """

    if header:
        # The YouTube channel uses different naming conventions that don't always
        # align with the Siskel/Roeper eras. For example, 1999 episodes are
        # sometimes titled "Siskel & Ebert". This regex handles multiple known
        # prefixes and is case-insensitive to handle typos like "SIskel".
        title = re.sub(
            r"((Siskel\s*&\s*Ebert|Ebert\s*&\s*Roeper|Roger Ebert & The Movies)\s*\(\d{4}\)\s*-\s*)",
            "", title, flags=re.IGNORECASE)
        # Remove leading numbers often present in YouTube titles
        title = re.sub(r"^\d+\s*", "", title)

        title = re.sub(r"\bth an\w*\s*", "", title, flags=re.IGNORECASE)

    parts = re.split(r'[|/]|(?<!\w)AND(?!\w)', title)

    movies = []

    for p in parts:

        if not p.strip():
            continue

        text = re.sub(r"\bincomplete episode\b|\bincomplete\b", "", p, flags=re.IGNORECASE)

        colon_index = text.find(":")
        dots_index = text.find("...")

        cut_points = [i for i in [colon_index, dots_index] if i != -1]

        if cut_points:
            text = text[:min(cut_points)]

        cleaned = text.lower().strip()

        if cleaned:
            movies.append(cleaned)

    return movies


def compare_lists(list_web, list_yt):
    """
    Calculates the number of fuzzy matches between two lists of movie titles.
    """

    return sum(
        any(ratio(pw, py) >= 0.8 for py in list_yt)
        for pw in list_web
    )


def is_incomplete(title):
    return "incomplete" in title.lower()


def find_match(web_episode_cleaned, source_list_processed):
    """
    Searches for a matching episode in a processed source list based on movie overlap.
    """

    for original_title, video_cleaned in source_list_processed:

        if compare_lists(web_episode_cleaned, video_cleaned) >= 2:
            return original_title, is_incomplete(original_title)

    return None, None


def total_movies(web_videos, header=False, roeper=False):
    """
    Counts the total number of individual movies across a list of episode strings.
    """

    total = 0

    for entry in web_videos:
        movies = clean_title(entry, header=header, roeper=roeper)
        total += len(movies)

    return total


def compare_titles(primary_episode_list,
                   website_episode_list,
                   youtube_episode_list=None,
                   roeper=False):
    """
    Reconciles the primary episode list (TVDB) with website and YouTube lists.
    
    Args:
        primary_episode_list (list): Main episode list (TVDB).
        website_episode_list (list): Episodes from website archive.
        youtube_episode_list (list): Episodes from YouTube.
        roeper (bool): If True, assumes Ebert & Roeper era.
    """

    results = []

    if not roeper and website_episode_list:
        website_processed = [
            (line, clean_title(line, header=False, roeper=roeper))
            for line in website_episode_list
        ]
    else:
        website_processed = []

    yt_processed = [
        (line, clean_title(line, header=True, roeper=roeper))
        for line in youtube_episode_list
    ] if youtube_episode_list else None

    for primary_episode in primary_episode_list:

        if not re.search(r'[^0-9]/[^0-9]', primary_episode):
            continue

        primary_cleaned = clean_title(primary_episode, header=False, roeper=roeper)

        if not roeper:
            match_web, inc_web = find_match(primary_cleaned, website_processed)
        else:
            match_web, inc_web = None, None

        if youtube_episode_list is not None:

            match_yt, inc_yt = find_match(primary_cleaned, yt_processed)

            if match_yt and match_web:

                inc = inc_yt and inc_web

                if not inc:
                    match = match_yt if not inc_yt else match_web
                else:
                    match = match_yt

                source = "both"

            elif match_yt:
                match, inc, source = match_yt, inc_yt, "youtube"

            elif match_web:
                match, inc, source = match_web, inc_web, "web"

            else:
                match, inc, source = None, is_incomplete(primary_episode), "none"

        else:

            if match_web:
                match, inc, source = match_web, inc_web, "web"
            else:
                match, inc, source = None, is_incomplete(primary_episode), "none"

        status = "match" if match else "no-match"

        results.append((primary_episode, match, status, source, inc))

    return results