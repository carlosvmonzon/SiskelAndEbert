from modules.names_reviews import create_data as update_review_site_data
from modules.names_tvdb import create_data as update_tvdb_data
from modules.names_youtube import create_data as update_youtube_data
from modules.preprocessing import open_files, compare_titles
from modules.html_writer import write_html
from modules.stats import stats

""" selector: 158, 157, 162, 7799""" 
#update_review_site_data()  The site is down by now, but the data was archived in data/archived_website_episodes.txt
""" sneak-previews,
at-the-movies-1982
siskel-and-ebert-at-the-movies (this and next)
""" 

# --- CONFIGURATION ---
# Set to True to run for Ebert & Roeper, False for Siskel & Ebert.
# This flag controls which data files are used and generated.
ROEPER_MODE = True
# --- END CONFIGURATION ---

# Set parameters based on the mode
if ROEPER_MODE:
    print("Running in Ebert & Roeper mode.")
    # Parameters for scraping Ebert & Roeper episodes from TVDB
    tvdb_update_params = {'min_i': 592, 'max_i': None, 'output_path': 'data/tvdb_roeper_episodes.txt'}
    tvdb_filepath = 'data/tvdb_roeper_episodes.txt'
    website_filepath = None  # No archived website data for the Roeper era
else:
    print("Running in Siskel & Ebert mode.")
    # Parameters for scraping Siskel & Ebert episodes from TVDB
    # Assuming default min/max parameters for update_tvdb_data are for Siskel & Ebert
    tvdb_update_params = {'output_path': 'data/tvdb_episodes.txt'}
    tvdb_filepath = 'data/tvdb_episodes.txt'
    website_filepath = 'data/archived_website_episodes.txt'

update = input('Do you want to update the data files? (Y/n): ').strip().lower()
if update in ('y', ''):
    print("🔄 Creating data files...")
    # The siskelebert.org site is down, but its data was archived.
    # To re-scrape, you would run: update_review_site_data()

    # Update TVDB data with mode-specific parameters
    print(f"Updating TVDB data for {'Ebert & Roeper' if ROEPER_MODE else 'Siskel & Ebert'}...")
    update_tvdb_data(**tvdb_update_params)

    # YouTube data is the same for both modes
    print("Updating YouTube video titles...")
    update_youtube_data()

# Load data files for the selected mode
print(f"Loading data from '{tvdb_filepath}'...")
if website_filepath:
    loaded_data = open_files(tvdb_filepath, "data/videos_youtube.txt", website_filepath)
    tvdb_episodes, youtube_videos, website_episodes = loaded_data
else:
    # No website data to load for Roeper mode
    loaded_data = open_files(tvdb_filepath, "data/videos_youtube.txt")
    tvdb_episodes, youtube_videos = loaded_data
    website_episodes = None

print("Comparing episode lists...")
results = compare_titles(tvdb_episodes, website_episodes, youtube_videos, roeper=ROEPER_MODE)

print("Generating HTML report...")
write_html(results, roeper=ROEPER_MODE)

print("Calculating statistics...")
stats(results, tvdb_episodes)

print("\n✅ Process complete.")
