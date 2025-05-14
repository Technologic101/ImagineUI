import json
import os
from pathlib import Path

def update_metadata_files():
    base_dir = Path('data_collection/scraped_designs')
    
    # Iterate through all numbered directories
    for dir_path in base_dir.iterdir():
        if not dir_path.is_dir() or not dir_path.name.isdigit():
            continue
            
        metadata_path = dir_path / 'metadata.json'
        if not metadata_path.exists():
            continue
            
        # Read existing metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Add image paths
        metadata['desktop_image'] = f"{dir_path.name}/screenshot_desktop.png"
        metadata['mobile_image'] = f"{dir_path.name}/screenshot_mobile.png"
        
        # Write updated metadata
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

if __name__ == '__main__':
    update_metadata_files() 