import os        
        
# Install required libraries        
os.system('pip install -r requirements.txt')        
        
# Run the scrapers        
os.system('python mecp_scraper.py')        
os.system('python competitor_scraper.py')        
        
# Run the SKU mapper        
os.system('python sku_mapper.py')        
        
# Run the price comparer        
os.system('python price_comparer.py')        
        
print("All scripts completed successfully.")        
os.system('pip install webdriver-manager')      
