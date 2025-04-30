# ETF Component Stocks Scraper

## Description
This pull request adds a Python script to scrape ETF component stocks information from the Shanghai Stock Exchange website and save it as a CSV file.

## Features
- Scrapes component stocks information from SSE ETF detail pages
- Supports any ETF fund ID
- Saves data to CSV format
- Provides command-line interface for easy use
- Includes error handling and documentation

## Implementation Details
- Uses Selenium with Chrome WebDriver for web scraping
- Extracts component stocks table from the ETF detail page
- Handles different table structures and formats
- Provides detailed logging for troubleshooting

## Files Added
- `etf_scraper_final.py`: Main script for ETF component stocks scraping
- `etf_api_scraper.py`: Alternative approach using API (not fully functional)
- `etf_selenium_scraper.py`: Initial Selenium implementation
- `etf_table_scraper.py`: Table extraction implementation
- `etf_scraper.py`: Initial script
- `etf_scraper_server.py`: Web server approach (not fully implemented)
- `README.md`: Documentation for usage and installation

## Testing
The script has been tested with multiple ETF IDs, including:
- 511090 (国债ETF)
- 510050 (50ETF)

## Dependencies
- Python 3.6+
- pandas
- selenium
- Chrome browser
- ChromeDriver