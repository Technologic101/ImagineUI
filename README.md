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

  I want a tool that can show me examples of a design I'm imagining.

### Audience:

  This app is for designers and non-designers who want to be inspired and see examples of good style design.

## Solution

  An agentic RAG application that scrapes designs from CSS Zen Garden and serves the best matches to the user.


# **Data Collection & Dataset Creation**

To populate the data, run the notebook in the data_collection folder with a range of design ids. Not all are included in the repository. New data will need to be moved to the src data folder to be accessible to the application.

# **Build**

uv sync

chainlit run src/app.py

And you're off!

## Public addresses

https://huggingface.co/spaces/Technologic101/imagineui

https://github.com/Technologic101/ImagineUI/tree/main


