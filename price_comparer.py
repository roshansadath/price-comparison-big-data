import os          
import pandas as pd          
import sqlite3          
import logging      
      
logging.basicConfig(filename='sku_mapper.log', level=logging.INFO)      
      
try:      
    # Load the mapping table          
    mapping_table = pd.read_csv('sku_mapping.csv')          
          
    # Connect to the databases          
    mecp_conn = sqlite3.connect('mecp_output/mecp.db')          
    competitor_conn = sqlite3.connect('lifesupply_output/lifesupply.db')          
          
    # Create the matched products table          
    c = mecp_conn.cursor()          
    c.execute('''CREATE TABLE IF NOT EXISTS matched_products          
                 (mecp_sku text, competitor_sku text)''')          
          
    # Match the SKUs          
    c.execute("SELECT sku FROM products")          
    mecp_skus = [row[0] for row in c.fetchall()]          
    for mecp_sku in mecp_skus:          
        # Look up the SKU in the mapping table          
        competitor_sku = mapping_table.loc[mapping_table['mecp_sku'] == mecp_sku, 'competitor_sku'].values[0]          
        if pd.isna(competitor_sku):          
            # If no matching SKU is found, prompt the user to enter a manual match          
            competitor_sku = input(f"No matching SKU found for {mecp_sku}. Please enter a competitor SKU: ")          
        # Save the matched SKU to the database          
        c.execute("INSERT INTO matched_products VALUES (?, ?)", (mecp_sku, str(competitor_sku)))          
          
    # Commit the changes and close the connections          
    mecp_conn.commit()          
    mecp_conn.close()          
    competitor_conn.close()          
          
    logging.info("SKU mapper completed successfully.")          
except Exception as e:      
    logging.error(f"Error occurred: {e}")      
