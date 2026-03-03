from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

def create_data(selector=612, output_path='data/archived_website_episodes.txt'):
    # Set up the WebDriver (in this case, with Chrome)
    driver = webdriver.Chrome()  # Make sure the path is correct

    # Load the web page
    driver.get('https://siskelebert.org/')

    # Wait for the page to load completely
    time.sleep(2)

    # Find the element that activates the "Disney Years" submenu
    submenu_toggle = driver.find_element(By.CSS_SELECTOR, f"#menu-item-{selector} .cm-submenu-toggle")

    # Click the submenu button to expand the list
    submenu_toggle.click()

    # Wait for the submenu to expand
    time.sleep(1)

    # Find all links within the submenu
    links = driver.find_elements(By.CSS_SELECTOR, f'#menu-item-{selector} .sub-menu li a')

    # Open the file in write mode
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        # Iterate over each link and visit the corresponding page
        for link in links:
            url = link.get_attribute('href')
            print(f"Visiting page: {url}")
            
            # Open the link
            driver.get(url)
            
            # Wait for the page to load
            time.sleep(2)
            
            try:
                # Find the container that holds the names, which has the class 'elementor-widget-container'
                containers = driver.find_elements(By.CSS_SELECTOR, '.elementor-widget-container p')
                
                # Iterate over each container and extract the text
                for container in containers:
                    name = container.text.strip()
                    if name:  # Make sure the text is not empty
                        # Replace commas with slashes
                        modified_name = name.replace(',', '/')
                        # Write the name to the file
                        file.write(modified_name + '\n')
            
            except Exception as e:
                print(f"Error getting names from {url}: {e}")
            
            # Go back to the main page after processing each link
            driver.back()
            
            # Wait a bit before moving to the next link
            time.sleep(1)

    # Close the browser
    driver.quit()