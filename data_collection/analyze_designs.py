import os
import json
from pathlib import Path
import asyncio
import base64
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

VISION_MODEL = "gpt-4o-2024-08-06"

client = AsyncOpenAI()

async def analyze_screenshot(design_id: str, design_path: Path):
    """Analyze screenshots and return description, categories, and visual characteristics"""
    try:
        # Check files exist
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
        
        # Get response first
        response = await client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert graphic designer analyzing print and web designs for aesthetics, functionality, audience appeal, and potential applications.
                    
                    The design should be considered from a visual standpoint. Use chain of thought to consider color palette, visual layout, typography, artistic style, mood, and potential applications.
                    Consider gradients, texture, background effects, and the use of images.
                    
                    Treat all text content as placeholder Lorem Ipsum.
                    
                    Provide analysis in clean JSON format with these exact keys:
                    {
                        "description": "A one-paragraph summary highlighting exceptional features of the design",
                        "categories": ["category1", "category2"],
                        "visual_characteristics": ["characteristic1", "characteristic2"]
                    }
                    Provide 4-6 categories and 4-6 visual characteristics most relevant to the style and feel of the design. Do not reference css or web design directly because this analysis is primarily about design. These lists should describe the design to another LLM that will use this data to generate a UI.
                    """
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this visual design. Output only the JSON object."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{desktop_base64}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{mobile_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        # Then get the content
        response_content = response.choices[0].message.content.strip()
        
        # Ensure the response is not empty
        if not response_content:
            print(f"Empty response for design {design_id}")
            return design_id, None, None, None
        
        # Extract JSON content from markdown code block
        if "```json" in response_content:
            # Remove the ```json prefix and ``` suffix
            response_content = response_content.split("```json")[1].split("```")[0].strip()
        
        # Parse the JSON response
        try:
            analysis = json.loads(response_content)
            
            # Update metadata with all fields
            metadata.update(analysis)
            
            # Save updated metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Successfully analyzed design {design_id}")
            # Return visual_characteristics as fourth element
            return design_id, analysis["description"], analysis["categories"], analysis["visual_characteristics"]
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for design {design_id}: {str(e)}")
            return design_id, None, None, None
        
    except Exception as e:
        print(f"Error processing design {design_id}: {str(e)}")
        return design_id, None, None, None

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