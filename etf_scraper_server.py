import pandas as pd
import time
import re
import csv
import os
import json
from flask import Flask, request, jsonify, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# HTML template for the main page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ETF Component Stocks Scraper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ETF Component Stocks Scraper</h1>
        <p>Enter the ETF fund ID to retrieve its component stocks information.</p>
        
        <div class="form-group">
            <label for="fund_id">ETF Fund ID:</label>
            <input type="text" id="fund_id" name="fund_id" placeholder="e.g., 511090" value="511090">
        </div>
        
        <button onclick="scrapeData()">Retrieve Component Stocks</button>
        
        <div id="loading" class="loading">
            <p>Loading data... This may take a few moments.</p>
        </div>
        
        <div id="error" class="error"></div>
        
        <div id="result" class="result" style="display: none;">
            <h2>Component Stocks</h2>
            <p id="download_link"></p>
            <div id="table_container"></div>
        </div>
    </div>
    
    <script>
        function scrapeData() {
            const fundId = document.getElementById('fund_id').value.trim();
            if (!fundId) {
                document.getElementById('error').textContent = 'Please enter a fund ID';
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').textContent = '';
            
            fetch(`/scrape?fund_id=${fundId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.error) {
                        document.getElementById('error').textContent = data.error;
                        return;
                    }
                    
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('download_link').innerHTML = `<a href="/download?fund_id=${fundId}" download>Download as CSV</a>`;
                    
                    // Create table
                    let tableHtml = '<table><thead><tr>';
                    for (const header of data.headers) {
                        tableHtml += `<th>${header}</th>`;
                    }
                    tableHtml += '</tr></thead><tbody>';
                    
                    for (const row of data.data) {
                        tableHtml += '<tr>';
                        for (const cell of row) {
                            tableHtml += `<td>${cell}</td>`;
                        }
                        tableHtml += '</tr>';
                    }
                    
                    tableHtml += '</tbody></table>';
                    document.getElementById('table_container').innerHTML = tableHtml;
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').textContent = 'An error occurred while retrieving data. Please try again.';
                    console.error('Error:', error);
                });
        }
    </script>
</body>
</html>
"""

# Store scraped data in memory
scraped_data = {}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape')
def scrape():
    fund_id = request.args.get('fund_id', '511090')
    
    try:
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to the URL
            url = f"https://www.sse.com.cn/assortment/fund/list/etfinfo/basic/index.shtml?FUNDID={fund_id}"
            driver.get(url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Find the section with the component stocks information
            wait = WebDriverWait(driver, 15)
            component_section = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '成份股信息内容')]"))
            )
            
            # Find the parent element that contains the table
            parent_element = component_section.find_element(By.XPATH, "./ancestor::div[contains(@class, 'sse_wrap_bd')]")
            
            # Find the table within the parent element
            table = parent_element.find_element(By.TAG_NAME, "table")
            
            # Extract table headers
            headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]
            
            # Extract table rows
            rows = []
            for tr in table.find_elements(By.TAG_NAME, "tr")[1:]:  # Skip the header row
                row_data = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                if row_data:  # Skip empty rows
                    rows.append(row_data)
            
            # Store the data
            scraped_data[fund_id] = {
                'headers': headers,
                'data': rows
            }
            
            return jsonify({
                'headers': headers,
                'data': rows
            })
        
        except Exception as e:
            return jsonify({'error': f"Error occurred: {str(e)}"})
        
        finally:
            # Close the browser
            driver.quit()
    
    except Exception as e:
        return jsonify({'error': f"Failed to initialize browser: {str(e)}"})

@app.route('/download')
def download():
    fund_id = request.args.get('fund_id', '511090')
    
    if fund_id not in scraped_data:
        return "Data not found. Please scrape the data first.", 404
    
    # Create a CSV string
    csv_data = []
    csv_data.append(','.join(scraped_data[fund_id]['headers']))
    
    for row in scraped_data[fund_id]['data']:
        # Escape any commas in the data
        escaped_row = [f'"{cell}"' if ',' in cell else cell for cell in row]
        csv_data.append(','.join(escaped_row))
    
    csv_string = '\n'.join(csv_data)
    
    # Set headers for CSV download
    headers = {
        'Content-Disposition': f'attachment; filename=etf_{fund_id}_components.csv',
        'Content-Type': 'text/csv'
    }
    
    return csv_string, 200, headers

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12000, debug=True)