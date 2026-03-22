import re
from Levenshtein import ratio
from modules.names_youtube import search_youtube

def open_files(*file_paths):
    names_text = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                names_text.append([line.strip() for line in file if line.strip()])
        except FileNotFoundError:
            print(f"File not found: {file_path}. Creating '{file_path}'...")
    return names_text

def clean_title(title, header=False):
    """
    Cleans and splits a raw episode title string into a list of individual movie titles.
    """
    if header:
        # Remove specific Season/Episode headers (e.g., Ebert & Roeper - S16E43 -)
        title = re.sub(r"(Ebert\s*&\s*Roeper|Siskel\s*&\s*Ebert).*?S\d+\s*E\d+\s*-\s*", "", title, flags=re.IGNORECASE)
        
        # Remove standard show prefixes (e.g. "Siskel & Ebert (1990) -", "Ebert & Roeper -")
        title = re.sub(r"^(Siskel\s*&\s*Ebert|Ebert\s*&\s*Roeper|Roger Ebert & The Movies)(\s*\(\d{4}\))?\s*(-|:)\s*", "", title, flags=re.IGNORECASE)
        
        # Remove common artifacts: trailing year, leading numbers/symbols, "th anniversary" remnants
        title = re.sub(r"\s*\(\d{4}\)$", "", title)
        title = re.sub(r"^\d+\s*", "", title)
        title = re.sub(r"^[\W_]+", "", title)
        title = re.sub(r"\bth an\w*\s*", "", title, flags=re.IGNORECASE)

    # Determine delimiter: pipe, slash, or comma (if others are absent)
    if '|' in title:
        pattern = r'[|]|(?<!\w)AND(?!\w)'
    elif '/' in title:
        pattern = r'[/]|(?<!\w)AND(?!\w)'
    else:
        # Split by comma UNLESS it is surrounded by digits (e.g. 3,000)
        # Matches comma if NOT followed by digit OR NOT preceded by digit
        pattern = r',(?!\d)|(?<!\d),|(?<!\w)AND(?!\w)'

    parts = re.split(pattern, title)
    movies = []

    for p in parts:
        if not p.strip():
            continue

        # Remove "incomplete" markers
        text = re.sub(r"\bincomplete( episode)?\b", "", p, flags=re.IGNORECASE)

        # Truncate at colon or ellipsis (often descriptions or subtitles)
        for marker in [":", "..."]:
            if marker in text:
                text = text.split(marker)[0]

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
        movies = clean_title(entry, header=header)
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
            (line, clean_title(line, header=False))
            for line in website_episode_list
        ]
    else:
        website_processed = []

    yt_processed = [
        (line, clean_title(line, header=True))
        for line in youtube_episode_list
    ] if youtube_episode_list else None

    for primary_episode in primary_episode_list:

        if not re.search(r'[^0-9]/[^0-9]', primary_episode):
            continue

        primary_cleaned = clean_title(primary_episode, header=False)

        if not roeper:
            match_web, inc_web = find_match(primary_cleaned, website_processed)
        else:
            match_web, inc_web = None, None

        if youtube_episode_list is not None:

            match_yt, inc_yt = find_match(primary_cleaned, yt_processed)

            if not match_yt and not match_web:
                # Attempt to search YouTube globally if not found in the channel
                query_prefix = "Ebert" if roeper else "Siskel & Ebert"
                # Remove leading numbering (e.g., "1 ") and replace slashes with spaces for the query
                clean_query_text = re.sub(r"^\d+\s*", "", primary_episode).replace("/", " ")
                search_query = f"{query_prefix} {clean_query_text}"
                
                print(f"🔎 Searching YouTube for: '{clean_query_text}'...")
                found_title = search_youtube(search_query)
                
                if found_title:
                    found_cleaned = clean_title(found_title, header=True)
                    if compare_lists(primary_cleaned, found_cleaned) >= (1 if roeper else 2):
                        match_yt = found_title
                        inc_yt = is_incomplete(found_title)
                        print(f"   ✅ Found online match: {found_title}")
                    else:
                        print(f"   ❌ Result not close enough: {found_title}")
                else:
                    print("   ❌ No video found.")

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