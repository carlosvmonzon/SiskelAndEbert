import re
from collections import defaultdict
import numpy as np
from modules.preprocessing import clean_title, total_movies

def count_year(results, web_videos):
    """
    Analyzes the results to group episodes by year based on matched titles (usually from YouTube).
    It assumes the input list is chronological.
    """
    year_counts = defaultdict(int)      # total entries assigned per year (titles)
    movie_counts = defaultdict(int)     # total movies (can be multiple per entry)
    unmatched_counts = defaultdict(int) # number of EPISODES without match per year (1 per no-match entry)
    # Regex to find year in parentheses, e.g., (1990), but not if followed by / (to avoid dates in titles like 20/20)
    year_pattern = re.compile(r"\((\d{4})\)(?!/)")
    current_year = None
    pending_entries = []  # store tuples (original_title, status)

    for original_title, matched_title, status, _, _ in results:
        # If we find a "match" title containing a year, update current_year
        if status == "match" and matched_title:
            match = year_pattern.search(matched_title)
            if match:
                detected_year = match.group(1)
                
                # If this is the first year detected, assume all pending entries belong to the previous year.
                # This handles the start of the list where year info might be missing until a match occurs.
                if current_year is None:
                    prev_year = str(int(detected_year) - 1)
                    for pending_title, pending_status in pending_entries:
                        year_counts[prev_year] += 1
                        movie_counts[prev_year] += len(clean_title(pending_title, header=False))
                        # Now add 1 per episode if it's not a match
                        if pending_status != "match":
                            unmatched_counts[prev_year] += 1
                    pending_entries.clear()

                current_year = detected_year

        # If we haven't detected any year yet, accumulate in pending (saving status)
        if current_year is None:
            pending_entries.append((original_title, status))
        else:
            # Assign the entry to current_year
            year_counts[current_year] += 1
            movie_counts[current_year] += len(clean_title(original_title, header=False))
            # If the entry has no match, count 1 episode without match
            if status != "match":
                unmatched_counts[current_year] += 1

    # If no year was detected in any match by the end, keep the original error
    if current_year is None:
        raise ValueError("❌ No year found in any matched title. Cannot assign years.")

    # Print by year: totals and no-match (1 per episode)
    print("\n📅 Movies per year (entries / movies / episodes without match):")
    for year in sorted(year_counts):
        total_entries = year_counts[year]
        total_movies_year = movie_counts[year]
        no_match_episodes = unmatched_counts.get(year, 0)
        print(f"{year}: episodes={total_entries}, movies={total_movies_year}, no_match={no_match_episodes}")

    # Calculate overall statistics
    overall_total_movies = total_movies(web_videos)
    print(f"\nTotal movies: {overall_total_movies}")
    # Estimate total movies if every episode had exactly 5 movies (common for Siskel & Ebert)
    print(f"Total movies (assuming 5 per episode): {sum(year_counts.values()) * 5}")
    print(f"Average titles per year: {np.median(list(year_counts.values())):.2f}")
    print(f"Average movies per year: {np.median(list(movie_counts.values())):.2f}")

def match_summary(results):
    """
    Prints a summary of matches by status and source (e.g., match_youtube, no-match_none).
    """
    match_counts = defaultdict(int)
    for _, _, status, source, _ in results:
        key = f"{status}_{source}"
        match_counts[key] += 1
    print("\n✅ Match Summary:")
    for key in sorted(match_counts):
        print(f"{key}: {match_counts[key]}")

def completion_rate(results, web_videos):
    """
    Calculates and prints the completion rate based on individual movie titles matched.
    """
    # Count episodes marked as incomplete (where only some segments were found)
    incomplete_count = sum(1 for _, _, status, _, inc in results if status == "match" and inc)
    print(f"\n⚠️ Incomplete matches: {incomplete_count}")
    
    # Sum the number of movies in matched episodes
    matched_titles = sum(
        len(clean_title(web_episode, header=False))
        for web_episode, _, status, _, _ in results if status == "match"
    )
    
    # Total movies in the source list (TVDB)
    total = total_movies(web_videos)
    if total > 0:
        print(f"\n📊 Estimated Completion Rate: {matched_titles} / {total} = {matched_titles / total:.2%}")
    else:
        print("\n📊 Estimated Completion Rate: 0 / 0 = 0.00%")

def stats(results, web_videos):
    # Main calls
    count_year(results, web_videos)
    match_summary(results)
    completion_rate(results, web_videos)