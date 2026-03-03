from modules.names_reviews import create_data as update_review_site_data
from modules.names_tvdb import create_data as update_tvdb_data
from modules.names_youtube import create_data as update_youtube_data
from modules.preprocessing import open_files, compare_titles
from modules.html_writer import write_html
from modules.stats import stats
    
update = input('Do you want to update the data files? (Y/n): ').strip().lower()
if update in ('y', ''):
    print("🔄 Creating data files...")
    """ selector: 158, 157, 162, 7799""" 
    #update_review_site_data() # The site is down by now, but the data was archived in data/archived_website_episodes.txt
    """ sneak-previews,
    at-the-movies-1982
    siskel-and-ebert-at-the-movies (this and next)
    """ 
    update_tvdb_data()
    
    update_youtube_data()
    

tvdb_episodes, youtube_videos, website_episodes = open_files("data/tvdb_episodes.txt",
                                                               "data/videos_youtube.txt",
                                                               "data/archived_website_episodes.txt")


results = compare_titles(tvdb_episodes, website_episodes, youtube_videos)

html = write_html(results)

stats(results, tvdb_episodes)