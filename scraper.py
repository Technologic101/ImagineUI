import os
import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def create_design_directory(design_id):
    """Create a directory for the design if it doesn't exist"""
    directory = f"designs/{design_id}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def save_css(url, directory):
    """Download and save CSS file"""
    response = requests.get(url)
    css_path = f"{directory}/style.css"
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(response.text)

def save_metadata(metadata, directory):
    """Save design metadata as JSON"""
    metadata_path = f"{directory}/metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def take_screenshot(url, directory):
    """Take screenshots of the design at desktop and mobile widths"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Desktop screenshot (1920px width)
    driver.set_window_size(1920, 1080)
    driver.get(url)
    # Wait for page to load and get full height
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1920, total_height)
    driver.save_screenshot(f"{directory}/screenshot_desktop.png")
    
    # Mobile screenshot (480px width)
    driver.set_window_size(480, 1080)
    driver.get(url)
    # Wait for page to load and get full height
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(480, total_height)
    driver.save_screenshot(f"{directory}/screenshot_mobile.png")
    
    driver.quit()

def scrape_design(design_id):
    """Scrape a single design"""
    # Create base URLs
    design_url = f"https://www.csszengarden.com/{design_id}"
    css_url = f"https://www.csszengarden.com/{design_id}/{design_id}.css"
    
    # Create directory for this design
    directory = create_design_directory(design_id)
    
    # Get design page
    response = requests.get(design_url)
    print(f"Response status: {response.status_code}")
    
    # Debug HTML content
    print("\nFirst 500 characters of response:")
    print(response.text[:500])
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Debug found elements
    print("\nFound elements:")
    print(f"h1: {soup.select_one('h1')}")
    print(f"author: {soup.select_one('meta[name=\"author\"]')}")
    
    # Extract metadata with error handling
    try:
        metadata = {
            "id": design_id,
            "author": soup.select_one('meta[name="author"]')["content"] if soup.select_one('meta[name="author"]') else "Unknown Author",
            "url": design_url,
            "css_url": css_url
        }
    except Exception as e:
        print(f"\nError extracting metadata: {str(e)}")
        raise
    
    # Save everything
    save_css(css_url, directory)
    save_metadata(metadata, directory)
    take_screenshot(design_url, directory)

def main():
    """Main function to scrape multiple designs"""
    # Create designs directory if it doesn't exist
    if not os.path.exists("designs"):
        os.makedirs("designs")
    
    # List of design IDs to scrape
    design_ids = ["221", "220", "219"]  # Add more IDs as needed
    
    for design_id in design_ids:
        try:
            print(f"Scraping design {design_id}...")
            scrape_design(design_id)
            print(f"Successfully scraped design {design_id}")
        except Exception as e:
            print(f"Error scraping design {design_id}: {str(e)}")

if __name__ == "__main__":
    main() 