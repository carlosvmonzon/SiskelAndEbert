# Siskel & Ebert Episode Matcher

This project scrapes and reconciles episode lists for two eras of the famous movie review show:
1.  **Siskel & Ebert**: The original run with Gene Siskel and Roger Ebert.
2.  **Ebert & Roeper**: The subsequent run with Roger Ebert and Richard Roeper.

It compares episode data from various sources (TheTVDB, an archived fan site, a YouTube channel, and a Rumble playlist) to find matches, identify incomplete episodes, and generate statistics and HTML reports.

## Data Sources

- **YouTube Channel**: [The Misadventures of Siskel & Ebert](https://www.youtube.com/@TheMisadventuresofSiskelEbert/videos)
- **Website**: siskelebert.org (Note: Site is currently down, but data is archived in `data/archived_website_episodes.txt`)
- **Rumble Playlist**: [Siskel & Ebert/Roeper/At The Movies](https://rumble.com/playlists/SiDwtb-VFMQ) — used as a last-resort fallback (see below)

## Matching fallback order

For each TVDB episode, a match is looked for in this order:
1. The archived website list / local YouTube channel data (instant, no network calls).
2. A lookup by exact TVDB air date against the pre-scraped Rumble playlist (`rumble_scraper.py`). Rumble's videos are titled with just a date (e.g. "Siskel & Ebert: 3-28-87"), not the movies reviewed, so this step matches on date rather than title.
3. A live YouTube search by episode title (via `search_youtube` in `names_youtube.py`) — only performed when you choose to update the data files (see below).

Rumble is behind Cloudflare and blocks plain HTTP scraping, so `rumble_scraper.py` uses Selenium (a real browser) to load and scroll the playlist once; the result is cached in `data/rumble_episodes.txt` and reused across runs instead of being re-scraped per episode.

## Project Structure

- `main.py`: The entry point of the application.
- `modules/`: Contains the scraping, processing, and reporting logic.
  - `names_tvdb.py`: Scrapes episode lists (and air dates) from TheTVDB.
  - `names_youtube.py`: Scrapes video titles from the YouTube channel and searches YouTube for individual episodes.
  - `rumble_scraper.py`: Scrapes the Rumble playlist (via Selenium) into a date → URL lookup, used as a fallback when an episode isn't found on YouTube.
  - `preprocessing.py`: Cleans titles and compares lists to find matches.
  - `html_writer.py`: Generates an HTML report of the match results.
  - `stats.py`: Calculates and prints statistics about the matches.
- `data/`: Stores the scraped text data.
  - `tvdb_episodes.txt` / `tvdb_roeper_episodes.txt`: The episode lists from TheTVDB.
  - `tvdb_episodes_dates.txt` / `tvdb_roeper_episodes_dates.txt`: The matching air dates for each line in the files above.
  - `videos_youtube.txt`: Video titles from the YouTube channel.
  - `archived_website_episodes.txt`: An archived list from the `siskelebert.org` fan site.
  - `rumble_episodes.txt`: `date\turl` pairs scraped from the Rumble playlist.

## Installation

1. Clone the repository.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```bash
python main.py
```

The script will first ask if you want to update the data files by re-scraping the sources.
- Answering **Y** (or Enter) re-scrapes TVDB, YouTube, and the Rumble playlist, then also enables the live YouTube search fallback (step 3 above) for episodes still unmatched afterward. If that re-scrape adds air dates to the Rumble playlist that weren't there before, the console prints those as new Rumble matches are applied.
- Answering **n** reuses the existing data files as-is and skips the live YouTube search fallback entirely — only the local website/YouTube/Rumble data is used to match episodes.

Based on the configuration in `main.py`, it will then:
1.  Perform the comparison for either "Siskel & Ebert" or "Ebert & Roeper".
2.  Generate an HTML report (`semantic_matches.html` or `roeper_matches.html`) with the results.
3.  Print a statistical summary to the console, including match counts and completion rates.

You can configure which comparison to run by editing the parameters in `main.py`.
```
