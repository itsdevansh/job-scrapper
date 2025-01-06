import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import ollama
import json

def parse_date(date_str):
    """Convert date strings to datetime objects"""
    try:
        return datetime.strptime(date_str.strip(), '%B %Y')
    except:
        return None

def calculate_duration(start_date, end_date):
    """Calculate duration between two dates in months"""
    if not (start_date and end_date):
        return 0
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

def extract_skills_categories(resume_text):
    """Use Ollama to categorize skills from resume"""
    prompt = f"""
    Analyze these skills from the resume and categorize them into these groups:
    1. Programming Languages
    2. Frameworks & Libraries
    3. Tools & Platforms
    4. Cloud & Infrastructure
    
    Skills to categorize:
    {resume_text}
    
    Return the result as a JSON string with these exact category names as keys and lists as values.
    """
    
    response = ollama.generate('llama2', prompt)
    # Extract JSON from response
    try:
        skills_json = json.loads(response['response'])
        return skills_json
    except:
        return None

def create_skills_distribution_plot(skills_dict):
    """Create a horizontal bar chart showing skills distribution"""
    plt.figure(figsize=(12, 6))
    
    # Prepare data
    categories = []
    counts = []
    for category, skills in skills_dict.items():
        categories.append(category)
        counts.append(len(skills))
    
    # Create horizontal bar chart
    y_pos = range(len(categories))
    plt.barh(y_pos, counts)
    plt.yticks(y_pos, categories)
    
    plt.title('Skills Distribution by Category')
    plt.xlabel('Number of Skills')
    
    return plt

def create_experience_timeline(experiences):
    """Create a timeline visualization of work experience"""
    plt.figure(figsize=(12, 6))
    
    companies = []
    durations = []
    start_dates = []
    
    for exp in experiences:
        companies.append(exp['company'])
        start = parse_date(exp['start_date'])
        end = parse_date(exp['end_date'])
        duration = calculate_duration(start, end)
        durations.append(duration)
        start_dates.append(start)
    
    # Create horizontal bar chart
    y_pos = range(len(companies))
    plt.barh(y_pos, durations)
    plt.yticks(y_pos, companies)
    
    plt.title('Work Experience Timeline (in months)')
    plt.xlabel('Duration (months)')
    
    return plt

# Example usage
resume_text = """
[Your resume text here]
"""

# Extract skills using Ollama
skills_dict = extract_skills_categories(resume_text)

# Create visualizations
if skills_dict:
    skills_plot = create_skills_distribution_plot(skills_dict)
    skills_plot.savefig('skills_distribution.png')

# Example work experience data
experiences = [
    {'company': 'Huawei Technologies', 'start_date': 'May 2024', 'end_date': 'December 2024'},
    {'company': 'Accenture and uOttawa', 'start_date': 'January 2024', 'end_date': 'April 2024'},
    {'company': 'Samsung R&D Institute', 'start_date': 'November 2021', 'end_date': 'October 2022'}
]

timeline_plot = create_experience_timeline(experiences)
timeline_plot.savefig('experience_timeline.png')