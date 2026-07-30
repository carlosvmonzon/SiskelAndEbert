import os
import re
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Matches the "M-D-YY" (or "MM-DD-YY") date embedded in Rumble's video URL slugs,
# e.g. ".../siskel-and-ebert-3-28-87.html" or ".../ebert-and-roeper-and-the-movies-1-20-01.html"
DATE_IN_SLUG = re.compile(r"-(\d{1,2})-(\d{1,2})-(\d{2})(?:-|\.html)")

# The playlist also contains guest-appearance clips from OTHER shows that happen to
# mention Siskel/Ebert (e.g. "the-oprah-winfrey-show-12-21-91-siskel-and-ebert"), plus
# an unrelated 2008+ revival with different hosts ("At the Movies with the Two Bens").
# Only accept slugs whose show name (right after the video ID) is one of the program's
# own historical titles, so a guest-clip sharing an air date can't shadow the real episode.
GENUINE_SHOW_PREFIX = re.compile(
    r"^v[0-9a-z]+-(sneak-previews|roger-ebert-and-the-movies|siskel-and-ebert|ebert-and-roeper|at-the-movies)-",
    re.IGNORECASE,
)
TWO_BENS_REVIVAL = re.compile(r"two-bens", re.IGNORECASE)

PLAYLIST_URL = "https://rumble.com/playlists/SiDwtb-VFMQ"


def _is_genuine_episode_url(url):
    slug = url.split("?")[0].rsplit("/", 1)[-1]
    if TWO_BENS_REVIVAL.search(slug):
        return False
    return bool(GENUINE_SHOW_PREFIX.match(slug))


def _parse_date_from_url(url):
    """Extracts the air date embedded in a Rumble video URL slug, e.g. '3-28-87' -> date(1987, 3, 28)."""
    slug = url.split("?")[0]
    match = DATE_IN_SLUG.search(slug)
    if not match:
        return None

    month, day, year_2digit = (int(g) for g in match.groups())
    year = 1900 + year_2digit if year_2digit >= 50 else 2000 + year_2digit
    try:
        return datetime(year, month, day).date()
    except ValueError:
        return None


def scrape_playlist_urls(playlist_url=PLAYLIST_URL, headless=True, max_scrolls=60, stable_rounds_to_stop=4):
    """
    Loads a Rumble playlist page with a real browser (Rumble is behind Cloudflare and
    blocks plain HTTP requests) and scrolls it to trigger lazy-loading until no new
    videos appear, collecting every video URL in the playlist.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(playlist_url)
        time.sleep(3)

        seen_urls = set()
        stable_rounds = 0
        last_count = 0
        for _ in range(max_scrolls):
            items = driver.find_elements(By.CSS_SELECTOR, "a.videostream__link")
            seen_urls |= {item.get_attribute("href") for item in items}

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.2)

            if len(seen_urls) == last_count:
                stable_rounds += 1
                if stable_rounds >= stable_rounds_to_stop:
                    break
            else:
                stable_rounds = 0
            last_count = len(seen_urls)

        return sorted(seen_urls)
    finally:
        driver.quit()


def create_data(playlist_url=PLAYLIST_URL, output_path="data/rumble_episodes.txt"):
    """Scrapes the Rumble playlist once and saves 'YYYY-MM-DD\\turl' lines, one per video found."""
    urls = scrape_playlist_urls(playlist_url)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for url in urls:
            if not _is_genuine_episode_url(url):
                continue
            date = _parse_date_from_url(url)
            if date:
                f.write(f"{date.isoformat()}\t{url}\n")


def load_rumble_dates(file_path="data/rumble_episodes.txt"):
    """Loads the scraped Rumble data into a dict of {date(YYYY-MM-DD): url}."""
    dates = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                date_str, url = line.split("\t", 1)
                dates[date_str] = url
    except FileNotFoundError:
        print(f"⚠️ File not found: {file_path}. Skipping Rumble fallback.")
    return dates
