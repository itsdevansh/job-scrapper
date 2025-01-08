# Job Search Tool

A Python application that aggregates job listings from multiple job boards with two versions - one with resume matching (LLM-powered) and one without.

## Features

- Scrapes jobs from LinkedIn, Indeed, ZipRecruiter, Glassdoor, and Google Jobs
- Two versions:
  - `agentic-main.py`: Full version with resume matching and LLM analysis
  - `main2.py`: Basic version without LLM features
- Customizable search filters (remote, job type, location)
- Export results to Excel

## Requirements

For basic version (`main2.py`):
```
jobspy
pandas
openpyxl
```

For LLM version (`agentic-main.py`), additional requirements:
```
PyPDF2
python-docx
langchain-ollama
```

## Installation

1. Clone the repository
2. Install dependencies:

Basic version:
```bash
pip install jobspy pandas openpyxl
```

LLM version:
```bash
pip install jobspy pandas PyPDF2 python-docx openpyxl langchain-ollama
```

For LLM version only:
- Install Ollama: Visit [Ollama's website](https://ollama.ai)
- Pull the model: `ollama pull llama3.2`

## Usage

Basic version (no LLM):
```bash
python main2.py
```

LLM version with resume matching:
```bash
python agentic-main.py
```

In the GUI:
- Select job boards to search
- Enter search term and location
- Upload resume (LLM version only)
- Set filters (remote, job type, etc.)
- Click "Search Jobs"

Results Export:
- Basic version: Excel file with job details
- LLM version: Color-coded Excel with match categories (Must Apply/Should Apply/Not Apply)

## File Structure

- `agentic-main.py`: Full version with LLM and resume matching
- `main2.py`: Basic version without LLM features
- `jobs.py`: Core job scraping implementation
