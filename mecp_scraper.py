import os            
import logging            
import time            
import requests            
from woocommerce import API            
  
logging.basicConfig(filename='mecp_scraper.log', level=logging.INFO)            
  
try:            
    # Create the output directory if it doesn't exist            
    if not os.path.exists('mecp_output'):            
        os.makedirs('mecp_output')            
  
    # Connect to the WooCommerce API            
    url = 'https://teamapharma.com/wp-json/wc/v3/products'            
    consumer_key = 'ck_5534284390c9db21b274c98466da4399ea2db7bd'            
    consumer_secret = 'cs_aa80d749fab631e6c99748e7a1f80d35d3193851'            
    wcapi = API(url=url, consumer_key=consumer_key, consumer_secret=consumer_secret)            
  
    # Create the products table in the database            
    wcapi.post("products", {            
        "name": "MECP Products",            
        "type": "simple",            
        "description": "MECP Products",            
        "short_description": "MECP Products",            
        "sku": "mecp",            
        "regular_price": "0.00",            
        "manage_stock": True,            
        "stock_quantity": 0            
    })            
  
    # Get all products from the API            
    products = wcapi.get("products").json()            
    print(products)      
  
    # Initialize counters for processed products and errors            
    processed_products = 0          
    errors = 0          
  
    # Extract product information from all products            
    for product in products:  
        try:  
            title = product['name']            
            description = product['description']            
            sku = product['sku']            
            price = float(product['regular_price'])            
            # Save the data to the database            
            # Replace this with your own code to save the data to your database            
            logging.info(f"Scraped product: {title} ({product['permalink']}) at {time.strftime('%Y-%m-%d %H:%M:%S')}.")            
            # Add a delay between requests based on the server response time            
            delay = requests.get(product['permalink']).elapsed.total_seconds() * 0.1            
            time.sleep(delay)          
            processed_products += 1          
        except Exception as e:          
            error_msg = f"Error processing product {product['name']}: {e}"        
            logging.error(error_msg)        
            print(error_msg)        
            errors += 1          
  
    logging.info(f"MECP scraper completed successfully. Processed {processed_products} products with {errors} errors.")          
except requests.exceptions.RequestException as e:            
    error_msg = f"Error occurred: {e}"        
    logging.error(error_msg)        
    print(error_msg)        
except Exception as e:            
    error_msg = f"Unknown error occurred: {e}"        
    logging.error(error_msg)        
    print(error_msg)  
