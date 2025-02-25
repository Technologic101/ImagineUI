---
title: ImagineUI
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: apache-2.0
---

# ImagineUI

An AI-powered CSS style generator that creates and iterates on designs using natural language instructions.

## Problem & Solution

### Problem
Designers and developers need a tool that can:
- Translate verbal descriptions into CSS styling
- Rapidly prototype and iterate on web layouts
- Learn from real-world design patterns

### Target Audience
- Frontend developers needing quick style prototypes
- UI/UX designers exploring creative variations
- Writers and content creators
- Small business owners creating marketing materials
- Cross-disciplinary teams discussing design concepts

### Solution
An agentic RAG application that:
- Consumes HTML templates
- Creates style variations based on natural language input
- Iterates designs through user feedback
- Learns from CSS Zen Garden designs

## Setup

This project uses Poetry for dependency management.

### Prerequisites

1. Python 3.11 (via brew or your system's package manager)
2. Poetry: `curl -sSL https://install.python-poetry.org | python3 -`

### Installation

1. Clone and enter the repository:
```
git clone https://github.com/yourusername/ImagineUI.git
cd ImagineUI
```

2. Install dependencies:
```
poetry install
poetry run playwright install chromium
```

## Tools

### CSS Zen Garden Scraper

Collects designs from CSS Zen Garden into a structured dataset. Each design in `designs/<design_id>/` contains:
- `style.css`: The design's CSS file
- `metadata.json`: Design information (author, URLs)
- `screenshot_desktop.png`: Screenshot at 1920px width
- `screenshot_mobile.png`: Screenshot at 480px width

Usage:
```
poetry run python scraper.py          # Run scraper
poetry run python analyze_designs.py   # Analyze designs
poetry run jupyter notebook           # Test in notebook
```

## Development

- `poetry add <package>`: Add dependencies
- `poetry update`: Update dependencies
- `poetry shell`: Activate virtual environment

## Project Structure

```
ImagineUI/
├── designs/            # Scraped CSS Zen Garden designs
│   └── <design_id>/   # Each design's files
├── scraper.py         # CSS Zen Garden scraper
├── test_scraper.ipynb # Scraper testing notebook
├── pyproject.toml     # Project dependencies
└── README.md
```

## Technical Stack

- LLM: For understanding design instructions
- Embedding Model: For design similarity search
- Vector Database: For storing design patterns
- Orchestration: For managing the design workflow
- Monitoring & Evaluation: For quality assurance
- User Interface: For interaction and feedback

# AI Designer

## Problem and Audience

### Problem:

  I want a tool that can use verbal instructions to prototype and iterate on a design for a UI or document.

### Audience:

  This app is for designers and non-designers who want to create UIs or documents using natural language. Examples include:

  - Styling a resume using a standardized template
  - Brand designers who want to iterate through ideas
  - Writers who want to present content in a visually engaging way
  - Creators of presentations and educational materials
  - Small business owners creating marketing materials

  The app will be particularly useful for cross-disciplinary web development teams discussing design concepts with stakeholders, to provide visual reference and preliminary materials for designs.

  
## Solution

  An agentic RAG application will be able to consume a template of html data, and create creative style variations based on input and feedback discussed with the user.

### Tools

a: LLM
b: Embedding Model
c: Orchestration
d: Vector Database
e: Monitoring
f: Evaluation
g: User Interface
h: Serving & Inference (optional)

Describe use of agents

# **Data Collection & Dataset Creation**

### Dataset Format
```json
{
  "id": "style_001",
  "html_template": "path/to/template.html",
  "css_style": "path/to/style.css",
  "screenshots": {
    "lg": "path/to/desktop.png",
    "sm": "path/to/mobile.png"
  },
  "metadata": {
    "description": "A minimalist business template with...",
    "category": ["business", "minimalist"],
    "accessibility_score": 98,
    "color_scheme": ["#ffffff", "#000000", "#4285f4"]
  }
}
```

### Data Collection Process
1. **Web Scraping**
   - Scrape CSS Zen Garden submissions
   - Collect associated screenshots
   - Extract design descriptions

2. **Manual Curation**
   - Review and categorize styles
   - Validate HTML/CSS combinations
   - Add detailed annotations

3. **Automated Processing**
   - Generate screenshots across viewports
   - Extract color schemes
   - Calculate accessibility scores

4. **Quality Assurance**
   - Validate file integrity
   - Check completeness of metadata
   - Verify screenshot quality

### Usage Guidelines
- Dataset is available under MIT License
- Proper attribution required for CSS Zen Garden content
- Screenshots may be used for training and testing
- Metadata can be extended with additional annotations

# **Build**  

## **Problem Worth Solving**  
Designing and styling web pages requires both creative and technical skills. Many developers and designers struggle with:  
- Translating verbal descriptions into CSS styling.  
- Rapidly prototyping and iterating on web layouts.  
- Learning from real-world design patterns without extensive manual effort.  

An **agentic CSS style creator** can bridge the gap by understanding style requests, generating layouts, and applying creative yet functional CSS designs.  

## **Potential LLM Solution**  
- **Multi-modal learning**: Utilize a dataset of CSS styles (from CSS Zen Garden) and their corresponding rendered outputs (screenshots).  
- **RAG-enhanced retrieval**: Combine existing UI pattern descriptions with CSS rules for better style understanding.  
- **Agentic workflow**: Allow the model to iteratively improve its design based on user feedback, tweaking layouts and styles dynamically.  
- **Dual input approach**: Users can either submit their own HTML or allow the agent to generate a basic layout.  

## **Target Audience**  
- **Frontend Developers** who need quick style prototypes.  
- **UI/UX Designers** looking to explore creative styles.  
- **No-Code/Low-Code Builders** who want AI-powered styling.  
- **Beginner Developers** learning CSS through interactive examples.  

## **Key Metrics**  
1. **Styling Accuracy** – How closely does the CSS match the user's description?  
2. **Creativity & Uniqueness** – Does it produce diverse and visually appealing results?  
3. **Functional Usability** – Are the generated styles accessible and responsive?  
4. **Iteration Success** – Does the model effectively refine the layout based on feedback?  
5. **RAGAS Scores** – To evaluate retrieval quality and grounding accuracy.  

## **Data Sources for RAG and Fine-Tuning**  
- **CSS Zen Garden Stylesheets** – To learn various aesthetic interpretations.  
- **Screenshots of Zen Garden pages** – For multi-modal association between styles and visuals.  
- **UI Pattern Dataset (with descriptions)** – To enhance textual understanding of design patterns.  
- **Generated CSS & User Feedback Loops** – To improve iteration quality.  

---

# **Share**  

## **Online Communities to Share Your Project In**  
- **r/web_design & r/frontend on Reddit** – Great for frontend developers and designers.  
- **Twitter/X (Hashtags: #CSS, #AI, #WebDev)** – To engage with the dev community.  
- **Dev.to & Hashnode** – For technical write-ups and project showcases.  
- **CodePen & Frontend Mentor Discords** – Where designers and developers share web experiments.  
- **LinkedIn Web Development Groups** – For professional feedback.  

### **Best Time to Share**  
- **Reddit**: 12 PM - 3 PM EST (high activity for tech subreddits).  
- **Twitter/X**: 9 AM - 12 PM PST (when devs engage most).  
- **Dev.to / Hashnode**: Post in the morning for better visibility.  
- **LinkedIn**: 8 AM - 10 AM EST (when professionals browse feeds).  


### CSS Zen Garden Scraping Tools

1. **Python-based Tools**
   - **Scrapy**
     - Robust framework for large-scale scraping
     - Handles JavaScript rendering
     - Built-in pipeline for downloading files
     ```python
     class ZenGardenSpider(scrapy.Spider):
         name = 'zengarden'
         start_urls = ['http://www.csszengarden.com/']
         
         def parse(self, response):
             for design in response.css('.design-selection li'):
                 yield {
                     'title': design.css('a::text').get(),
                     'css_url': design.css('a::attr(href)').get(),
                     'designer': design.css('.designer::text').get()
                 }
     ```

   - **Beautiful Soup 4**
     - Simpler alternative for static content
     - Good for parsing HTML/CSS structure
     - Easy integration with requests library

2. **Browser Automation**
   - **Playwright**
     - Modern alternative to Selenium
     - Better performance
     - Built-in screenshot and PDF generation

3. **CSS Processing Tools**
   - **PostCSS**
     - Parses and analyzes CSS
     - Extracts color schemes
     - Identifies design patterns
   - **StyleStats**
     - Generates CSS analytics
     - Measures complexity
     - Reports accessibility metrics

### Scraping Process

1. **Initial Setup**
   ```bash
   pip install scrapy beautifulsoup4 selenium playwright postcss-py
   ```

2. **Data Collection Steps**
   - Fetch main gallery page
   - Extract design links and metadata
   - Download CSS files
   - Capture screenshots at different viewports
   - Parse and analyze CSS properties

3. **Legal Considerations**
   - Respect robots.txt
   - Include appropriate delays between requests
   - Store attribution information
   - Follow CSS Zen Garden's terms of use

4. **Data Validation**
   - Verify CSS file integrity
   - Check image quality
   - Validate HTML structure
   - Ensure complete metadata
