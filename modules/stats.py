import re
from collections import defaultdict
import numpy as np
from modules.preprocessing import clean_title, total_movies

def stats(results, web_videos, roeper=False):
    def count_year(results):
        year_counts = defaultdict(int)      # total entradas asignadas por año (títulos)
        movie_counts = defaultdict(int)     # total películas (puede haber varios por entrada)
        unmatched_counts = defaultdict(int) # número de EPISODIOS sin match por año (1 por entrada no-match)
        year_pattern = re.compile(r"\((\d{4})\)(?!/)")

        current_year = None
        pending_entries = []  # guardamos tuplas (original_title, status)

        for original_title, matched_title, status, _, _ in results:
            # Si encontramos un título "match" que contenga año, actualizamos current_year
            if status == "match" and matched_title:
                match = year_pattern.search(matched_title)
                if match:
                    detected_year = match.group(1)

                    # Si no había año previo, asignamos los pendientes al año anterior
                    if current_year is None:
                        prev_year = str(int(detected_year) - 1)
                        for pending_title, pending_status in pending_entries:
                            year_counts[prev_year] += 1
                            movie_counts[prev_year] += len(clean_title(pending_title, header=False))
                            # Ahora sumamos 1 por episodio si no es match
                            if pending_status != "match":
                                unmatched_counts[prev_year] += 1
                        pending_entries.clear()

                    current_year = detected_year

            # Si aún no hemos detectado ningún año, acumulamos en pendientes (guardando status)
            if current_year is None:
                pending_entries.append((original_title, status))
            else:
                # Asignamos la entrada al current_year
                year_counts[current_year] += 1
                movie_counts[current_year] += len(clean_title(original_title, header=False))
                # Si la entrada no tiene match, contamos 1 episodio sin match
                if status != "match":
                    unmatched_counts[current_year] += 1

        # Si al final no se detectó ningún año en ningún match, mantenemos el error original
        if current_year is None:
            raise ValueError("❌ No year found in any matched title. Cannot assign years.")

        # Imprimimos por año: totales y no-match (1 por episodio)
        print("\n📅 Películas por año (entradas / películas / episodios sin match):")
        for year in sorted(year_counts):
            total_entries = year_counts[year]
            total_movies_year = movie_counts[year]
            no_match_episodes = unmatched_counts.get(year, 0)
            print(f"{year}: episodes={total_entries}, movies={total_movies_year}, no_match={no_match_episodes}")

        overall_total_movies = total_movies(web_videos)
        print(f"\nTotal movies: {overall_total_movies}")
        print(f"Total movies (assuming 5 per episode): {sum(year_counts.values()) * 5}")
        print(f"Average titles per year: {np.median(list(year_counts.values())):.2f}")
        print(f"Average movies per year: {np.median(list(movie_counts.values())):.2f}")

    def match_summary(results):
        match_counts = defaultdict(int)
        for _, _, status, source, _ in results:
            key = f"{status}_{source}"
            match_counts[key] += 1

        print("\n✅ Match Summary:")
        for key in sorted(match_counts):
            print(f"{key}: {match_counts[key]}")

    def completion_rate(results):
        incomplete_count = sum(1 for _, _, status, _, inc in results if status == "match" and inc)
        print(f"\n⚠️ Incomplete matches: {incomplete_count}")
        matched_titles = sum(
            len(clean_title(web_episode, header=False))
            for web_episode, _, status, _, _ in results if status == "match"
        )
        total = total_movies(web_videos)
        print(f"\n📊 Estimated Completion Rate: {matched_titles} / {total} = {matched_titles / total:.2%}")

    if roeper:
        return

    # Llamadas principales
    count_year(results)
    match_summary(results)
    completion_rate(results)