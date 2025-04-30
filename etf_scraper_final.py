#!/usr/bin/env python3
"""
ETF Component Stocks Scraper

This script scrapes the component stocks information from the Shanghai Stock Exchange
ETF detail page and saves it as a CSV file.

Usage:
    python etf_scraper_final.py [fund_id]

Example:
    python etf_scraper_final.py 511090
"""

import pandas as pd
import time
import sys
import os
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """
    Set up and return a configured Chrome WebDriver
    
    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Initialize the WebDriver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome WebDriver: {str(e)}")
        sys.exit(1)

def scrape_etf_components(fund_id):
    """
    Scrape ETF component stocks information from Shanghai Stock Exchange website
    
    Args:
        fund_id (str): The fund ID, e.g., '511090'
        
    Returns:
        DataFrame: A pandas DataFrame containing the component stocks information
    """
    url = f"https://www.sse.com.cn/assortment/fund/list/etfinfo/basic/index.shtml?FUNDID={fund_id}"
    
    # Initialize the WebDriver
    driver = setup_driver()
    
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
        
        if not tables:
            print("No tables found on the page. The page structure might have changed.")
            return None
        
        # Look for the component stocks table
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
            
            if not rows:
                print("No rows found in the component stocks table.")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            print(f"Successfully extracted {len(df)} component stocks.")
            return df
        else:
            print("Could not find the component stocks table.")
            
            # If we couldn't find the table by header, try to find it by position
            # Based on previous observations, the 7th table (index 6) often contains the component stocks
            if len(tables) >= 7:
                print("Attempting to extract data from the 7th table...")
                table = tables[6]
                
                # Extract headers and rows
                headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]
                
                if not headers:
                    print("No headers found in the 7th table.")
                    return None
                
                print(f"7th table headers: {headers}")
                
                rows = []
                for tr in table.find_elements(By.TAG_NAME, "tr")[1:]:  # Skip the header row
                    row_data = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                    if row_data:  # Skip empty rows
                        rows.append(row_data)
                
                if not rows:
                    print("No rows found in the 7th table.")
                    return None
                
                # Create DataFrame
                df = pd.DataFrame(rows, columns=headers)
                
                print(f"Successfully extracted {len(df)} rows from the 7th table.")
                return df
            
            return None
    
    except TimeoutException:
        print("Timeout occurred while waiting for the page to load.")
        return None
    except NoSuchElementException as e:
        print(f"Element not found: {str(e)}")
        return None
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
    finally:
        # Close the browser
        driver.quit()

def save_to_csv(df, fund_id, output_dir=None):
    """
    Save the DataFrame to a CSV file
    
    Args:
        df (DataFrame): The DataFrame to save
        fund_id (str): The fund ID used in the filename
        output_dir (str, optional): Directory to save the CSV file. Defaults to current directory.
        
    Returns:
        str: Path to the saved CSV file, or None if saving failed
    """
    if df is not None and not df.empty:
        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, f"etf_{fund_id}_components.csv")
        else:
            filename = f"etf_{fund_id}_components.csv"
        
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving CSV file: {str(e)}")
            return None
    else:
        print("No data to save.")
        return None

def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
        Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Scrape ETF component stocks from Shanghai Stock Exchange')
    parser.add_argument('fund_id', nargs='?', default='511090', help='ETF fund ID (default: 511090)')
    parser.add_argument('-o', '--output-dir', help='Directory to save the CSV file')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    fund_id = args.fund_id
    output_dir = args.output_dir
    
    print(f"Scraping component stocks for ETF with ID: {fund_id}")
    
    # Scrape the data
    df = scrape_etf_components(fund_id)
    
    # Save to CSV
    if df is not None:
        filename = save_to_csv(df, fund_id, output_dir)
        if filename:
            print(f"Component stocks data has been saved to {filename}")
            
            # Display the first few rows
            print("\nFirst few rows of the data:")
            print(df.head())
    else:
        print("Failed to retrieve component stocks data.")
        sys.exit(1)

if __name__ == "__main__":
    main()