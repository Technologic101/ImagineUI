import os
import requests
from bs4 import BeautifulSoup
import json
from playwright.async_api import async_playwright
import asyncio

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

async def take_screenshot(url, directory):
    """Take screenshots of the design at desktop and mobile widths"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Desktop screenshot (1920px width)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto(url)
        # Get full height
        height = await page.evaluate('document.body.scrollHeight')
        await page.set_viewport_size({'width': 1920, 'height': int(height)})
        await page.screenshot(path=f"{directory}/screenshot_desktop.png", full_page=True)
        
        # Mobile screenshot (480px width)
        page = await browser.new_page(viewport={'width': 480, 'height': 1080})
        await page.goto(url)
        # Get full height
        height = await page.evaluate('document.body.scrollHeight')
        await page.set_viewport_size({'width': 480, 'height': int(height)})
        await page.screenshot(path=f"{directory}/screenshot_mobile.png", full_page=True)
        
        await browser.close()

async def scrape_design(design_id):
    """Scrape a single design"""
    # Create base URLs
    design_url = f"https://www.csszengarden.com/{design_id}"
    css_url = f"https://www.csszengarden.com/{design_id}/{design_id}.css"
    
    # Create directory for this design
    directory = create_design_directory(design_id)
    
    # Get design page
    response = requests.get(design_url)
    print(f"Response status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    author_meta = soup.select_one('meta[name="author"]')
    
    # Debug found elements
    print("\nFound elements:")
    print(f"h1: {soup.select_one('h1')['content']}")
    print(f"author: {author_meta['content']}")
    
    # Extract metadata with error handling
    try:
        metadata = {
            "id": design_id,
            "author": author_meta["content"] if author_meta else "Unknown Author",
            "url": design_url,
            "css_url": css_url
        }
    except Exception as e:
        print(f"\nError extracting metadata: {str(e)}")
        raise
    
    # Save everything
    save_css(css_url, directory)
    save_metadata(metadata, directory)
    await take_screenshot(design_url, directory)

async def main():
    """Main function to scrape multiple designs"""
    # Create designs directory if it doesn't exist
    if not os.path.exists("designs"):
        os.makedirs("designs")
    
    # List of design IDs to scrape
    design_ids = ["221", "220", "219"]  # Add more IDs as needed
    
    for design_id in design_ids:
        try:
            print(f"Scraping design {design_id}...")
            await scrape_design(design_id)
            print(f"Successfully scraped design {design_id}")
        except Exception as e:
            print(f"Error scraping design {design_id}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 