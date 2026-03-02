import requests, re
import os
from bs4 import BeautifulSoup
                
def obtener_episodios_tvdb(url):
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extraer los títulos de los episodios, eliminando la referencia de temporada/episodio (como S01E01)
    episodios = []
    
    # Aquí extraemos todos los <a> dentro de <li> con las clases que contienen los títulos de los episodios
    for i, episode in enumerate(soup.find_all("li", class_="list-group-item"), start=1):
        if i>591:
            continue      
        title_tag = episode.find("a")
        if title_tag:
            titulo_completo = title_tag.get_text(strip=True)  # Título completo con la referencia de temporada/episodio
            titulo_limpio = re.sub(r'S\d{2}E\d{2}', '', titulo_completo).strip()  # Eliminamos la referencia como S01E01
            episodios.append(str(i) + ' ' + titulo_limpio)
       

    return episodios

def create_data(url_snippet="siskel-and-ebert-at-the-movies", output_path="data/videos_web.txt"):
    # Obtener los títulos de los episodios de TVDB
    url = f"https://thetvdb.com/series/{url_snippet}/allseasons/official"
    videos_web = obtener_episodios_tvdb(url)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for video in videos_web:
            f.write(video + "\n")
