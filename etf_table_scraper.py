import pandas as pd
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_etf_components(fund_id):
    """
    Scrape ETF component stocks information from Shanghai Stock Exchange website
    
    Args:
        fund_id (str): The fund ID, e.g., '511090'
        
    Returns:
        DataFrame: A pandas DataFrame containing the component stocks information
    """
    url = f"https://www.sse.com.cn/assortment/fund/list/etfinfo/basic/index.shtml?FUNDID={fund_id}"
    
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the URL
        print(f"Accessing URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(10)
        
        # Print the page title to verify we're on the right page
        print(f"Page title: {driver.title}")
        
        # Find all tables on the page
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} tables on the page")
        
        # Based on previous output, Table 7 (index 6) contains the component stocks information
        # This is the table with headers like '证券代码', '证券简称', etc.
        component_table = None
        
        for i, table in enumerate(tables):
            headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]
            if headers and '证券代码' in headers:
                print(f"Found component stocks table at index {i}")
                component_table = table
                break
        
        if component_table:
            # Extract table headers
            headers = [th.text.strip() for th in component_table.find_elements(By.TAG_NAME, "th")]
            print(f"Table headers: {headers}")
            
            # Extract table rows
            rows = []
            for tr in component_table.find_elements(By.TAG_NAME, "tr")[1:]:  # Skip the header row
                row_data = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                if row_data:  # Skip empty rows
                    rows.append(row_data)
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            print(f"Successfully extracted {len(df)} component stocks.")
            return df
        else:
            print("Could not find the component stocks table.")
            return None
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
    finally:
        # Close the browser
        driver.quit()

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