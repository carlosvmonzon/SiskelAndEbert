import yt_dlp
import time
import os

def obtener_titulos_videos(channel_url, delay=2, roeper = False):
     
    """Obtiene todos los títulos de videos de un canal de YouTube, con un pequeño retraso opcional."""
    opciones = {
        'quiet': True,
        'extract_flat': 'in_playlist',
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        time.sleep(delay)  # Espera luego de la extracción
        titulos = [video['title'] for video in info.get('entries', [])]
        return sorted(titulos)

def guardar_titulos_en_archivo(titulos, ruta_archivo):
    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
    with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
        archivo.writelines(f"{titulo}\n" for titulo in titulos)

def create_data(roeper = False, channel_url = 'https://www.youtube.com/@TheMisadventuresofSiskelEbert/videos',
                salida='data/videos_youtube.txt'):
    if roeper:
        return
    titulos = obtener_titulos_videos(channel_url)
    guardar_titulos_en_archivo(titulos, salida)

if __name__ == '__main__':
    url = 'https://www.youtube.com/@TheMisadventuresofSiskelEbert/videos'
    create_data(roeper = False)
