import os  
import pandas as pd  
import sqlite3  
import logging  
from flask import Flask, render_template, request, redirect, url_for  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.metrics import accuracy_score  
  
app = Flask(__name__)  
  
logging.basicConfig(filename='sku_mapper.log', level=logging.INFO)  
  
@app.route('/')  
def index():  
    try:  
        # Load the mapping tables  
        mapping_tables = {}  
        mapping_tables['competitor1'] = pd.read_csv('competitor1_sku_mapping.csv')  
        mapping_tables['competitor2'] = pd.read_csv('competitor2_sku_mapping.csv')  
  
        # Connect to the databases  
        mecp_conn = sqlite3.connect('mecp_output/mecp.db')  
        competitor_conns = {}  
        competitor_conns['competitor1'] = sqlite3.connect('competitor1_output/competitor1.db')  
        competitor_conns['competitor2'] = sqlite3.connect('competitor2_output/competitor2.db')  
  
        # Create the matched products tables  
        c = mecp_conn.cursor()  
        for competitor in mapping_tables.keys():  
            c.execute(f'''CREATE TABLE IF NOT EXISTS {competitor}_matched_products  
                         (mecp_sku text, competitor_sku text)''')  
  
        # Train the models on the existing mapping tables  
        models = {}  
        for competitor, mapping_table in mapping_tables.items():  
            X = mapping_table['mecp_sku'].values.reshape(-1, 1)  
            y = mapping_table['competitor_sku']  
            model = RandomForestClassifier()  
            model.fit(X, y)  
            y_pred = model.predict(X)  
            accuracy = accuracy_score(y, y_pred)  
            models[competitor] = model  
            logging.info(f"Model for {competitor} trained with accuracy {accuracy}")  
  
        # Match the SKUs  
        c.execute("SELECT sku FROM products")  
        mecp_skus = [row[0] for row in c.fetchall()]  
        for mecp_sku in mecp_skus:  
            for competitor, mapping_table in mapping_tables.items():  
                # Look up the SKU in the mapping table  
                competitor_sku = mapping_table.loc[mapping_table['mecp_sku'] == mecp_sku, 'competitor_sku'].values[0]  
                if pd.isna(competitor_sku):  
                    # If no matching SKU is found, use the model to predict the competitor SKU  
                    competitor_sku = models[competitor].predict([[mecp_sku]])[0]  
                    # Save the predicted SKU to the database  
                    c.execute(f"INSERT INTO {competitor}_matched_products VALUES (?, ?)", (mecp_sku, str(competitor_sku)))  
  
        # Commit the changes and close the connections  
        mecp_conn.commit()  
        mecp_conn.close()  
        for conn in competitor_conns.values():  
            conn.close()  
  
        logging.info("SKU mapper completed successfully.")  
    except Exception as e:  
        logging.error(f"Error occurred: {e}")  
    return "SKU mapper completed successfully."  
  
@app.route('/manual_match', methods=['GET', 'POST'])  
def manual_match():  
    if request.method == 'POST':  
        mecp_sku = request.form['mecp_sku']  
        competitor_sku = request.form['competitor_sku']  
        competitor = request.form['competitor']  
        # Save the manual match to the database  
        mecp_conn = sqlite3.connect('mecp_output/mecp.db')  
        c = mecp_conn.cursor()  
        c.execute(f"INSERT INTO {competitor}_matched_products VALUES (?, ?)", (mecp_sku, competitor_sku))  
        mecp_conn.commit()  
        mecp_conn.close()  
        return redirect(url_for('index'))  
    else:  
        mecp_sku = request.args.get('mecp_sku')  
        competitors = list(mapping_tables.keys())  
        return render_template('manual_match.html', mecp_sku=mecp_sku, competitors=competitors)  
  
@app.route('/training_data')  
def training_data():  
    mapping_tables = {}  
    mapping_tables['competitor1'] = pd.read_csv('competitor1_sku_mapping.csv')  
    mapping_tables['competitor2'] = pd.read_csv('competitor2_sku_mapping.csv')  
    return render_template('training_data.html', mapping_tables=mapping_tables)  
  
@app.route('/add_competitor', methods=['GET', 'POST'])  
def add_competitor():  
    if request.method == 'POST':  
        competitor_name = request.form['competitor_name']  
        # Create the mapping table for the new competitor  
        mapping_table = pd.DataFrame(columns=['mecp_sku', f'{competitor_name}_sku'])  
        mapping_table.to_csv(f'{competitor_name}_sku_mapping.csv', index=False)  
        # Create the matched products table for the new competitor  
        mecp_conn = sqlite3.connect('mecp_output/mecp.db')  
        c = mecp_conn.cursor()  
        c.execute(f'''CREATE TABLE IF NOT EXISTS {competitor_name}_matched_products  
                     (mecp_sku text, {competitor_name}_sku text)''')  
        mecp_conn.commit()  
        mecp_conn.close()  
        return redirect(url_for('index'))  
    else:  
        return render_template('add_competitor.html')  
  
@app.route('/remove_competitor', methods=['GET', 'POST'])  
def remove_competitor():  
    if request.method == 'POST':  
        competitor_name = request.form['competitor_name']  
        # Remove the mapping table for the competitor  
        os.remove(f'{competitor_name}_sku_mapping.csv')  
        # Remove the matched products table for the competitor  
        mecp_conn = sqlite3.connect('mecp_output/mecp.db')  
        c = mecp_conn.cursor()  
        c.execute(f"DROP TABLE IF EXISTS {competitor_name}_matched_products")  
        mecp_conn.commit()  
        mecp_conn.close()  
        return redirect(url_for('index'))  
    else:  
        competitors = list(mapping_tables.keys())  
        return render_template('remove_competitor.html', competitors=competitors)  
  
if __name__ == '__main__':  
    # Load the mapping tables  
    mapping_tables = {}  
    mapping_tables['competitor1'] = pd.read_csv('competitor1_sku_mapping.csv')  
    mapping_tables['competitor2'] = pd.read_csv('competitor2_sku_mapping.csv')  
    app.run(debug=True)  
