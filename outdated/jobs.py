import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
from fake_useragent import UserAgent
import html

class JobScraper:
    def __init__(self, debug_mode: bool = False):
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if debug_mode else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize session with retry strategy
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # Rotate user agents
        self.ua = UserAgent()
        self.jobs_data = []
        self.debug_mode = debug_mode

    def get_headers(self) -> dict:
        """Generate new headers with rotating user agent."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text data."""
        if not text:
            return 'N/A'
        # Decode HTML entities
        text = html.unescape(text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        return text.strip()

    def format_date(self, date_str: str) -> str:
        """Convert various date formats to a standardized format."""
        try:
            date_str = date_str.lower().strip()
            
            # Handle "posted X days/hours ago" format
            if 'ago' in date_str:
                number = int(re.findall(r'\d+', date_str)[0])
                if 'day' in date_str:
                    date = datetime.now() - timedelta(days=number)
                elif 'hour' in date_str:
                    date = datetime.now() - timedelta(hours=number)
                elif 'week' in date_str:
                    date = datetime.now() - timedelta(weeks=number)
                elif 'month' in date_str:
                    date = datetime.now() - timedelta(days=number * 30)
                else:
                    date = datetime.now()
                return date.strftime('%Y-%m-%d')
            
            # Handle "Today" and "Yesterday"
            if 'today' in date_str:
                return datetime.now().strftime('%Y-%m-%d')
            if 'yesterday' in date_str:
                return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Try parsing various date formats
            for fmt in ['%Y-%m-%d', '%b %d, %Y', '%d %b %Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return datetime.now().strftime('%Y-%m-%d')
        except Exception as e:
            self.logger.warning(f"Date parsing error for '{date_str}': {str(e)}")
            return datetime.now().strftime('%Y-%m-%d')

    def scrape_linkedin(self, job_title: str, location: str = '', pages: int = 3) -> List[Dict]:
        """Scrape job listings from LinkedIn with pagination."""
        base_url = 'https://www.linkedin.com/jobs/search'
        
        for page in range(pages):
            try:
                search_params = {
                    'keywords': job_title,
                    'location': location,
                    'start': page * 25,  # LinkedIn uses 25 jobs per page
                    'sortBy': 'DD'
                }
                
                self.logger.info(f"Scraping LinkedIn page {page + 1}/{pages}")
                response = self.session.get(
                    base_url, 
                    params=search_params, 
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='job-search-card')
                    
                    if not job_cards:
                        self.logger.warning(f"No job cards found on LinkedIn page {page + 1}")
                        continue
                    
                    for card in job_cards:
                        try:
                            job_data = {
                                'platform': 'LinkedIn',
                                'title': self.clean_text(card.find('h3', class_='base-search-card__title').text if card.find('h3', class_='base-search-card__title') else 'N/A'),
                                'company': self.clean_text(card.find('h4', class_='base-search-card__subtitle').text if card.find('h4', class_='base-search-card__subtitle') else 'N/A'),
                                'location': self.clean_text(card.find('span', class_='job-search-card__location').text if card.find('span', class_='job-search-card__location') else 'N/A'),
                                'date_posted': self.format_date(card.find('time')['datetime'] if card.find('time') else datetime.now().strftime('%Y-%m-%d')),
                                'link': card.find('a', class_='base-card__full-link')['href'] if card.find('a', class_='base-card__full-link') else 'N/A',
                                'salary': self.clean_text(card.find('span', class_='job-search-card__salary-info').text if card.find('span', class_='job-search-card__salary-info') else 'Not specified')
                            }
                            self.jobs_data.append(job_data)
                        except Exception as e:
                            self.logger.warning(f"Error parsing LinkedIn job card: {str(e)}")
                            continue
                
                # Respect rate limits
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error scraping LinkedIn page {page + 1}: {str(e)}")
                continue
        
        return self.jobs_data

    def scrape_indeed(self, job_title: str, location: str = '', pages: int = 3) -> List[Dict]:
        """Scrape job listings from Indeed with pagination and debugging."""
        base_url = 'https://www.indeed.com/jobs'
        
        for page in range(pages):
            try:
                search_params = {
                    'q': job_title,
                    'l': location,
                    'sort': 'date',
                    'start': page * 10  # Indeed uses 10 jobs per page
                }
                
                self.logger.info(f"Scraping Indeed page {page + 1}/{pages}")
                response = self.session.get(
                    base_url, 
                    params=search_params, 
                    headers=self.get_headers(),
                    timeout=10
                )
                
                self.logger.debug(f"Indeed Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='job_seen_beacon')
                    
                    self.logger.debug(f"Found {len(job_cards)} job cards on Indeed page {page + 1}")
                    
                    if not job_cards:
                        # Try alternative class names
                        job_cards = soup.find_all('div', class_='tapItem')
                        self.logger.debug(f"Found {len(job_cards)} job cards using alternative class")
                    
                    for card in job_cards:
                        try:
                            # Enhanced selectors for Indeed's structure
                            title_elem = (
                                card.find('h2', class_='jobTitle') or 
                                card.find('a', class_='jcs-JobTitle')
                            )
                            company_elem = (
                                card.find('span', class_='companyName') or 
                                card.find('div', class_='company_location')
                            )
                            location_elem = (
                                card.find('div', class_='companyLocation') or 
                                card.find('div', class_='company_location')
                            )
                            date_elem = (
                                card.find('span', class_='date') or 
                                card.find('span', class_='date-posted')
                            )
                            
                            job_data = {
                                'platform': 'Indeed',
                                'title': self.clean_text(title_elem.text if title_elem else 'N/A'),
                                'company': self.clean_text(company_elem.text if company_elem else 'N/A'),
                                'location': self.clean_text(location_elem.text if location_elem else 'N/A'),
                                'date_posted': self.format_date(date_elem.text if date_elem else datetime.now().strftime('%Y-%m-%d')),
                                'link': 'https://www.indeed.com' + card.find('a')['href'] if card.find('a') else 'N/A',
                                'salary': self.clean_text(card.find('div', class_='salary-snippet').text if card.find('div', class_='salary-snippet') else 'Not specified')
                            }
                            self.jobs_data.append(job_data)
                        except Exception as e:
                            self.logger.warning(f"Error parsing Indeed job card: {str(e)}")
                            continue
                
                # Respect rate limits
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error scraping Indeed page {page + 1}: {str(e)}")
                continue
        
        return self.jobs_data

    def export_to_excel(self, filename: str = 'job_listings.xlsx'):
        """Export scraped job data to Excel file with enhanced formatting."""
        if not self.jobs_data:
            self.logger.warning("No data to export")
            return
        
        try:
            df = pd.DataFrame(self.jobs_data)
            
            # Sort by date and platform
            df = df.sort_values(['date_posted', 'platform'], ascending=[False, True])
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Job Listings')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Job Listings']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            self.logger.info(f"Data exported successfully to {filename}")
            self.logger.info(f"Total jobs found: {len(df)}")
            self.logger.info(f"Jobs per platform: {df['platform'].value_counts().to_dict()}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")

def main():
    # Get user input with validation
    while True:
        job_title = input("Enter the job title you're looking for: ").strip()
        if job_title:
            break
        print("Job title cannot be empty. Please try again.")
    
    location = input("Enter location (press Enter to skip): ").strip()
    
    while True:
        try:
            pages = input("Enter number of pages to scrape per platform (default is 3): ").strip()
            pages = int(pages) if pages else 3
            if pages > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    debug_mode = input("Enable debug mode? (y/n, default: n): ").lower().strip() == 'y'
    
    # Initialize scraper
    scraper = JobScraper(debug_mode=debug_mode)
    
    # Scrape jobs from multiple platforms
    print("\nScraping LinkedIn...")
    scraper.scrape_linkedin(job_title, location, pages)
    
    print("\nScraping Indeed...")
    scraper.scrape_indeed(job_title, location, pages)
    
    # Export results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'job_listings_{timestamp}.xlsx'
    scraper.export_to_excel(filename)

if __name__ == "__main__":
    main()