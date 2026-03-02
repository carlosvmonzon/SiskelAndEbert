from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

def create_data(selector=612, output_path='data/nombres_web.txt'):
    # Configura el WebDriver (en este caso, con Chrome)
    driver = webdriver.Chrome()  # Asegúrate de que la ruta sea correcta

    # Carga la página web
    driver.get('https://siskelebert.org/')

    # Espera a que la página cargue completamente
    time.sleep(2)

    # Encuentra el elemento que activa el submenú de "Disney Years"
    submenu_toggle = driver.find_element(By.CSS_SELECTOR, f"#menu-item-{selector} .cm-submenu-toggle")

    # Haz clic en el botón de submenú para desplegar la lista
    submenu_toggle.click()

    # Espera a que el submenú se despliegue
    time.sleep(1)

    # Encuentra todos los enlaces dentro del submenú
    enlaces = driver.find_elements(By.CSS_SELECTOR, f'#menu-item-{selector} .sub-menu li a')

    # Abrimos el archivo en modo escritura
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        # Itera sobre cada enlace y visita la página correspondiente
        for enlace in enlaces:
            url = enlace.get_attribute('href')
            print(f"Visitando la página: {url}")
            
            # Abre el enlace
            driver.get(url)
            
            # Espera a que la página cargue
            time.sleep(2)
            
            try:
                # Encuentra el contenedor que contiene los nombres, que tiene la clase 'elementor-widget-container'
                contenedores = driver.find_elements(By.CSS_SELECTOR, '.elementor-widget-container p')
                
                # Itera sobre cada contenedor y extrae el texto
                for contenedor in contenedores:
                    nombre = contenedor.text.strip()
                    if nombre:  # Asegúrate de que el texto no esté vacío
                        # Reemplaza las comas por barras
                        nombre_modificado = nombre.replace(',', '/')
                        # Escribe el nombre en el archivo
                        file.write(nombre_modificado + '\n')
            
            except Exception as e:
                print(f"Error al obtener los nombres en {url}: {e}")
            
            # Regresa a la página principal después de procesar cada enlace
            driver.back()
            
            # Espera un poco antes de pasar al siguiente enlace
            time.sleep(1)

    # Cierra el navegador
    driver.quit()