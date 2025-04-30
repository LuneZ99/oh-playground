import pandas as pd
import requests
import json
import re
import time
import csv
import os
import sys

def scrape_etf_components(fund_id):
    """
    Scrape ETF component stocks information from Shanghai Stock Exchange API
    
    Args:
        fund_id (str): The fund ID, e.g., '511090'
        
    Returns:
        DataFrame: A pandas DataFrame containing the component stocks information
    """
    # Set up headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Referer': 'https://www.sse.com.cn/',
        'Origin': 'https://www.sse.com.cn',
        'Host': 'query.sse.com.cn',
    }
    
    # The API endpoint for component stocks
    timestamp = int(time.time() * 1000)
    api_url = f"https://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback{timestamp}&isPagination=false&sqlId=FUND_CONSTITUENT_STOCK_DETAIL_SEARCH&FUNDID={fund_id}&_={timestamp}"
    
    try:
        print(f"Accessing API URL: {api_url}")
        response = requests.get(api_url, headers=headers)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve data: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        # Extract JSON data from JSONP response
        jsonp_text = response.text
        print(f"Response: {jsonp_text}")  # Print full response for debugging
        
        # Extract the JSON part from the JSONP response
        match = re.search(r'jsonpCallback\d+\((.*)\)', jsonp_text)
        if not match:
            print("Failed to extract JSON data from JSONP response")
            return None
            
        json_text = match.group(1)
        data = json.loads(json_text)
        
        # Extract the component stocks data
        component_stocks = data.get('result', [])
        
        if not component_stocks:
            print("No component stocks data found.")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(component_stocks)
        
        print(f"Successfully extracted {len(df)} component stocks.")
        return df
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def save_to_csv(df, fund_id):
    """
    Save the DataFrame to a CSV file
    
    Args:
        df (DataFrame): The DataFrame to save
        fund_id (str): The fund ID used in the filename
    """
    if df is not None and not df.empty:
        filename = f"etf_{fund_id}_components.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Data saved to {filename}")
        return filename
    else:
        print("No data to save.")
        return None

def main():
    # Default fund ID
    fund_id = "511090"
    
    # Allow user to specify a different fund ID
    if len(sys.argv) > 1:
        fund_id = sys.argv[1]
    else:
        user_input = input(f"Enter ETF fund ID (default is {fund_id}): ")
        if user_input.strip():
            fund_id = user_input.strip()
    
    print(f"Scraping component stocks for ETF with ID: {fund_id}")
    
    # Scrape the data
    df = scrape_etf_components(fund_id)
    
    # Save to CSV
    if df is not None:
        filename = save_to_csv(df, fund_id)
        if filename:
            print(f"Component stocks data has been saved to {filename}")
            
            # Display the first few rows
            print("\nFirst few rows of the data:")
            print(df.head())
    else:
        print("Failed to retrieve component stocks data.")

if __name__ == "__main__":
    main()