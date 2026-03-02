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

def clean_title(title, header=False):
    if header:
        title = re.sub(r"(Siskel & Ebert\s*\(\d{4}\)\s*-\s*|\d+\s*)", "", title)
        title = re.sub(r"\bth an\w*\s*", "", title, flags=re.IGNORECASE)
    parts = re.split(r'[|/]|(?<!\w)AND(?!\w)', title)
    
    movies = []
    for p in parts:
        if not p.strip():
            continue
        # Logic integrated from previous levenshtein_similarity function
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
    return sum(
        any(ratio(pw, py) >= 0.8 for py in list_yt)
        for pw in list_web
    )   

def is_incomplete(title):
    return "incomplete" in title.lower()

def find_match(web_episode_cleaned, source_list_processed):
    for original_title, video_cleaned in source_list_processed:
        if compare_lists(web_episode_cleaned, video_cleaned) >= 2:
            return original_title, is_incomplete(original_title)
    return None, None

def total_movies(web_videos, header=False):
    total = 0
    for entry in web_videos:
        movies = clean_title(entry, header=header)
        total += len(movies)
    return total

def compare_titles(web_videos, txt_names, youtube_videos=None):
    results = []
    
    # Pre-process data once to avoid re-cleaning in the loop
    txt_processed = [(line, clean_title(line, header=False)) for line in txt_names]
    yt_processed = [(line, clean_title(line, header=True)) for line in youtube_videos] if youtube_videos else None

    for web_episode in web_videos:
        if not re.search(r'[^0-9]/[^0-9]', web_episode):
            continue

        web_cleaned = clean_title(web_episode, header=False)

        match_web, inc_web = find_match(web_cleaned, txt_processed)

        if youtube_videos is not None:
            match_yt, inc_yt = find_match(web_cleaned, yt_processed)

            if match_yt and match_web:
                inc = inc_yt and inc_web  # Incomplete only if both are incomplete
                if not inc:
                    match = match_yt if not inc_yt else match_web
                else:
                    match = match_yt  # Default to youtube if both incomplete
                source = "both"
            elif match_yt:
                match, inc, source = match_yt, inc_yt, "youtube"
            elif match_web:
                match, inc, source = match_web, inc_web, "web"
            else:
                match, inc, source = None, is_incomplete(web_episode), "none"
        else:
            if match_web:
                match, inc, source = match_web, inc_web, "web"
            else:
                match, inc, source = None, is_incomplete(web_episode), "none"

        status = "match" if match else "no-match"
        results.append((web_episode, match, status, source, inc))

    return results