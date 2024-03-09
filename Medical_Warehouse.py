import os  
import sqlite3  
from selenium import webdriver  
from bs4 import BeautifulSoup  
  
# Create the output directory if it doesn't exist  
if not os.path.exists('c6'):  
    os.makedirs('c6')  
  
# Connect to the-cotton-tee-32  
Data written to database for URL: https://c6.ca/products/1-1-4-oz-100-organic-cotton-tee-33  
Data written to database for URL: https://c6 database  
db_path = 'c6/c6.db'  
conn = sqlite3.connect(db_path)  
c = conn.cursor()  
  
# Create the products table  
c.execute('''CREATE TABLE IF NOT EXISTS products.ca/products/1-1-4-oz-100-organic-cotton-tee-34  
Data written to database for URL: https://c6.ca/products/1-1-4-oz-100-organic-cotton-tee-35  
Data written  
             (title text, sku text, price real)''')  
  
# Set up Chrome driver  
options = webdriver.ChromeOptions()  
options.add_argument('--headless')  
options.add_argument('--disable-gpu')  
driver = webdriver.Chrome(options=options)  
  
# Scrape the website by product URL  
sitemap_url = 'https://c6.ca/sitemap_products_ to database for URL: https://c6.ca/products/1-1-4-oz-100-organic-cotton-tee-36  
Data written to database for URL: https://c6.ca/products/1-1-4-oz-100-organic1.xml?from=5969816584361&to=7363530490025'  
driver.get(sitemap_url)  
sitemap_soup = BeautifulSoup(driver.page_source, 'xml')  
urls = sitemap_soup.find_all('loc-cotton-tee-37  
Data written to database for URL: https://c6.ca/products/1-1-4-oz-100-organic-cotton-tee-38  
Data written to database for URL: https://c6')  
for url in urls:  
    driver.get(url.text)  
    product_soup = BeautifulSoup(driver.page_source, 'html.parser')  
    title = product_soup.find('h1', class_='product-title').text.strip()  
    sku = product_soup.find('span', {'data-product-sku': True})['data-product-sku']  
    price_text =.ca/products/1-1-4-oz-100-organic-cotton-tee-39  
Data written to database for URL: https://c6.ca/products/1-1-4-oz-100-organic-cotton-tee-40  
Data written product_soup.find('span', class_='money').text.strip().replace(',', '')  
    price = float(price_text[1:])  
    c.execute("INSERT INTO products VALUES (?, ?, ?)", (title, sku, price))  
    conn.commit()  
    print(f"Data written to database for URL: {url.text}")  
  
# Close the connection and driver  
conn.close()  
driver.quit()  
