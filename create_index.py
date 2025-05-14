import json
from pathlib import Path

def create_index():
    # Paths
    analyses_dir = Path('data_collection/analyses/detailed')
    output_file = Path('data_collection/dataset/index.json')
    
    # Dictionary to store all metadata
    index = {}
    
    # Iterate through all numbered directories
    for dir_path in analyses_dir.iterdir():
        if not dir_path.is_dir() or not dir_path.name.isdigit():
            continue
            
        metadata_path = dir_path / 'metadata.json'
        if not metadata_path.exists():
            continue
            
        # Read metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        # Add image paths
        metadata['desktop_img'] = f"{dir_path.name}_desktop.png"
        metadata['mobile_img'] = f"{dir_path.name}_mobile.png"
            
        # Add to index using the directory number as key
        index[dir_path.name] = metadata
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(exist_ok=True)
    
    # Write combined index
    with open(output_file, 'w') as f:
        json.dump(index, f, indent=2)

if __name__ == '__main__':
    create_index() 