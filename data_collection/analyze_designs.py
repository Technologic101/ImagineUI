import os
import json
from pathlib import Path
import asyncio
import base64
from openai import AsyncOpenAI
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from .prompts import get_prompt

load_dotenv()
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

VISION_MODEL = "claude-3-7-sonnet-20250219"

async def analyze_screenshot(design_id: str, design_path: Path, detailed: bool = True, output_path: Path = None):
    """
    Analyze screenshots and return description, categories, and visual characteristics
    
    Args:
        design_id (str): ID of the design to analyze
        design_path (Path): Path to the design's source files
        detailed (bool): Whether to use detailed or core analysis prompt
        output_path (Path): Path to save analysis results. If None, uses analyses/default
    
    Returns:
        tuple: (design_id, description, categories, visual_characteristics)
    """
    try:
        # Use output_path if provided, otherwise use default analyses path
        save_path = output_path or Path("analyses/default")
        
        # Ensure output directory exists
        if not save_path.exists():
            save_path.mkdir(parents=True, exist_ok=True)
            
        # Check source files exist
        metadata_path = design_path / "metadata.json"
        desktop_img = design_path / "screenshot_desktop.png"
        mobile_img = design_path / "screenshot_mobile.png"
        
        if not all(f.exists() for f in [metadata_path, desktop_img, mobile_img]):
            print(f"Missing required files for design {design_id}")
            return design_id, None, None, None
        
        # Load existing metadata
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # Read both images
        try:
            with open(desktop_img, "rb") as f:
                desktop_base64 = base64.b64encode(f.read()).decode('utf-8')
            with open(mobile_img, "rb") as f:
                mobile_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error reading images for design {design_id}: {str(e)}")
            return design_id, None, None, None
        
        print(f"Analyzing design {design_id}...")
        
        # Get response using specified detail level
        response = await client.messages.create(
            model=VISION_MODEL,
            max_tokens=8000 if detailed else 4000,  # More tokens for detailed analysis
            system=get_prompt(detailed=detailed),
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this visual design. Output only the JSON object."
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": desktop_base64
                        }
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": mobile_base64
                        }
                    }
                ]
            }]
        )
        
        response_content = response.content[0].text
        
        if not response_content:
            print(f"Empty response for design {design_id}")
            return design_id, None, None, None
        
        # Extract JSON content from markdown code block
        if "```json" in response_content:
            response_content = response_content.split("```json")[1].split("```")[0].strip()
        
        try:
            analysis = json.loads(response_content)
            
            # Create design-specific directory in output path
            design_output_path = save_path / design_id
            design_output_path.mkdir(parents=True, exist_ok=True)
            
            # Save metadata.json inside the design folder
            output_metadata_path = design_output_path / "metadata.json"
            
            # Save analysis to output path
            with open(output_metadata_path, "w") as f:
                json.dump(analysis, f, indent=2)
            
            print(f"Successfully analyzed design {design_id}")
            
            # Return appropriate fields based on detail level
            if detailed:
                return (
                    design_id,
                    analysis["description"]["summary"],
                    analysis["categories"],
                    analysis["visual_characteristics"]
                )
            else:
                return (
                    design_id,
                    analysis["description"],
                    analysis["categories"],
                    analysis["visual_characteristics"]
                )
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for design {design_id}: {str(e)}")
            return design_id, None, None, None
        
    except Exception as e:
        print(f"Error processing design {design_id}: {str(e)}")
        return design_id, None, None, None

async def attribute_designs():
    """
    Process scraped designs to extract title and author from CSS comments.
    Adds these attributes to the existing metadata.json files.
    Skips designs that already have both title and author.
    """
    designs_dir = Path("scraped_designs")
    
    if not designs_dir.exists():
        print("Scraped designs directory not found!")
        return
    
    # Get all design directories
    design_dirs = [d for d in designs_dir.iterdir() if d.is_dir()]
    
    if not design_dirs:
        print("No design directories found!")
        return
    
    print(f"Found {len(design_dirs)} designs to check")
    
    processed = 0
    skipped = 0
    failed = 0
    
    for design_dir in design_dirs:
        try:
            # Check for required files
            css_path = design_dir / "style.css"
            metadata_path = design_dir / "metadata.json"
            
            if not all(f.exists() for f in [css_path, metadata_path]):
                print(f"Missing required files for design {design_dir.name}")
                failed += 1
                continue
            
            # Check existing metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            # Skip if both title and author already exist and aren't default values
            if (metadata.get("title") and metadata.get("author") and 
                metadata["title"] != "Untitled" and metadata["author"] != "Unknown"):
                print(f"Skipping design {design_dir.name} - already attributed")
                skipped += 1
                continue
            
            # Read CSS file
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            
            # Extract title and author using Claude
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                system="You are a helpful assistant that extracts title and author information from CSS comments. Return ONLY a JSON object with 'title' and 'author' fields, nothing else.",
                messages=[{
                    "role": "user",
                    "content": f"Extract the title and author from these CSS comments. Return only the JSON object, no markdown:\n\n{css_content}"
                }]
            )
            
            # Get response text and clean it up
            response_text = response.content[0].text.strip()
            
            # Remove markdown formatting if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
                
            try:
                attribution = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for design {design_dir.name}. Response was:")
                print(response_text)
            
            # Update metadata
            metadata.update({
                "title": attribution.get("title", "Untitled"),
                "author": attribution.get("author", "Unknown")
            })
            
            # Save updated metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Successfully attributed design {design_dir.name}")
            print(f"Title: {attribution.get('title', 'Untitled')}")
            print(f"Author: {attribution.get('author', 'Unknown')}\n")
            processed += 1
            
        except Exception as e:
            print(f"Error processing design {design_dir.name}: {str(e)}")
            failed += 1
    
    print("\nAttribution complete!")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Total: {len(design_dirs)}")

async def main():
    designs_dir = Path("designs")
    
    if not designs_dir.exists():
        print("Designs directory not found!")
        return
    
    # Get all design directories
    design_dirs = [d for d in designs_dir.iterdir() if d.is_dir()]
    
    if not design_dirs:
        print("No design directories found!")
        return
    
    print(f"Found {len(design_dirs)} designs to analyze")
    
    # Create list of design IDs to analyze (001-050)
    design_ids = [f"{i:03d}" for i in range(1, 51)]
    
    # Analyze all designs
    tasks = []
    for design_dir in design_dirs:
        design_id = design_dir.name
        tasks.append(analyze_screenshot(design_id, design_dir))
    
    # Run analyses concurrently
    results = await asyncio.gather(*tasks)
    
    # Print summary
    successful = 0
    for design_id, desc, cats, _ in results:
        if desc is not None:
            successful += 1
            print(f"\nDesign {design_id}:")
            print(f"Description: {desc}")
            print(f"Categories: {', '.join(cats)}")
    
    print(f"\nSuccessfully analyzed {successful} out of {len(design_dirs)} designs")

if __name__ == "__main__":
    asyncio.run(main()) 