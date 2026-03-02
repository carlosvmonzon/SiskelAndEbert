from modules.names_reviews import create_data as create_data1
from modules.names_tvdb import create_data as create_data2
from modules.names_youtube import create_data as create_data3
from modules.preprocessing import open_files, compare_titles
from modules.html_writer import write_html
from modules.stats import stats
    
update = input('Do you want to update the data files? (Y/n): ').strip().lower()
if update in ('y', ''):
    print("🔄 Creating data files...")
    """ selector: 158, 157, 162, 7799"""
    #create_data1() # The site is down by now, but the data was archived in /data/videos_web.txt
    """ sneak-previews,
    at-the-movies-1982
    siskel-and-ebert-at-the-movies (this and next)
    """ 
    create_data2()
    
    create_data3()
    

web_videos, youtube_videos, txt_names = open_files("data/videos_web.txt", 
                                                    "data/videos_youtube.txt", 
                                                    "data/nombres_web.txt")


results = compare_titles(web_videos, txt_names, youtube_videos)

html = write_html(results)

stats(results, web_videos)