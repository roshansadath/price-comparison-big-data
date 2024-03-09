import os        
import sqlite3        
import requests        
from bs4 import BeautifulSoup        
import time        
import logging        
from selenium import webdriver        
from selenium.webdriver.support.ui import WebDriverWait        
from selenium.webdriver.support import expected_conditions as EC        
from selenium.webdriver.common.by import By        
from selenium.webdriver.common.alert import Alert        
from selenium.webdriver.chrome.service import Service        
from webdriver_manager.chrome import ChromeDriverManager        
        
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')        
        
def close_popup(driver):        
    try:        
        WebDriverWait(driver, 5).until(EC.alert_is_present())        
        alert = Alert(driver)        
        alert_text = alert.text        
        if "Don't show again" in alert_text:        
            alert.dismiss()        
        else:        
            alert.accept()        
    except:        
        pass        
        
def scrape_product(driver, url):        
    scraped_data = {}        
    driver.get(url)        
    close_popup(driver)        
    product_soup = BeautifulSoup(driver.page_source, 'html.parser')        
    try:        
        scraped_data['name'] = product_soup.find('h1', class_='productView-title').text.strip()        
    except:        
        scraped_data['name'] = 'N/A'        
        logging.warning(f"Product name not found for URL: {url}")        
    try:        
        scraped_data['description'] = product_soup.find('div', class_='productView-description').text.strip()        
    except:        
        scraped_data['description'] = 'N/A'        
        logging.warning(f"Product description not found for URL: {url}")        
    try:        
        scraped_data['sku'] = product_soup.find('dt', text='SKU:').find_next_sibling('dd').text.strip()        
    except:        
        scraped_data['sku'] = 'N/A'        
        logging.warning(f"Product SKU not found for URL: {url}")        
    try:        
        price_text = product_soup.find('span', class_='price--withoutTax').text.strip().replace(',', '')        
        scraped_data['price'] = float(price_text[4:])        
    except:        
        scraped_data['price'] = 0.0        
        logging.warning(f"Product price not found for URL: {url}")       
    try:        
        scraped_data['product_id'] = product_soup.find('dt', text='Product ID:').find_next_sibling('dd').text.strip()        
    except:        
        scraped_data['product_id'] = 'N/A'        
        logging.warning(f"Product ID not found for URL: {url}")        
    logging.info(f"Scraped product: {scraped_data} ({url}) at {time.strftime('%Y-%m-%d %H:%M:%S')}.")        
    return scraped_data        
       
        
try:        
    # Create the output directory if it doesn't exist        
    if not os.path.exists('lifesupply_output'):        
        os.makedirs('lifesupply_output')        
        
    # Connect to the database        
    db_path = 'lifesupply_output/lifesupply.db'  
    print(f"Database path: {db_path}")  
    with sqlite3.connect(db_path) as conn:        
        c = conn.cursor()        
        
        # Create the products table        
        c.execute('''CREATE TABLE IF NOT EXISTS products        
                     (name text, description text, sku text, price real)''')        
        
        # Scrape the website by product URL        
        url_prefix = 'https://lifesupply.ca'        
        options = webdriver.ChromeOptions()        
        options.add_argument('--disable-blink-features=AutomationControlled')        
        service = Service(ChromeDriverManager().install())        
        driver = webdriver.Chrome(service=service, options=options)        
        scraped_urls = set()        
        for page in range(1, 8):        
            sitemap_url = f'https://lifesupply.ca/xmlsitemap.php?type=products&page={page}'        
            sitemap_response = requests.get(sitemap_url)        
            sitemap_soup = BeautifulSoup(sitemap_response.content, 'xml')        
            urls = sitemap_soup.find_all('loc')        
            for url in urls:        
                product_url = url.text        
                if product_url not in scraped_urls:        
                    scraped_data = scrape_product(driver, product_url)        
                    c.execute("INSERT INTO products VALUES (?, ?, ?, ?)", (scraped_data['name'], scraped_data['description'], scraped_data['sku'], scraped_data['price']))        
                    conn.commit()  # commit changes after each insert  
                    print(f"Data written to database for URL: {product_url}")  
                    scraped_urls.add(product_url)        
                    if len(scraped_urls) >= 100000: # limit to 1000 products      
                        break      
            if len(scraped_urls) >= 1000:      
                break      
        
        # Commit the changes and close the connection        
        conn.commit()        
        logging.info("Competitor scraper completed successfully.")        
finally:        
    driver.quit()  
