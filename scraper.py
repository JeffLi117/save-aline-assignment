#!/usr/bin/env python3
"""
Web Scraper for Technical Knowledge Base
========================================
Goal: Crawl a given website (blogs, guides, etc.), extract clean article content,
convert to Markdown, and return JSON in the required format.

Usage:
    python scraper.py https://quill.co/blog
    python scraper.py interviewing.io
"""

import requests
from bs4 import BeautifulSoup
import trafilatura
import json
import re
from urllib.parse import urljoin, urlparse, urlunparse
from tqdm import tqdm
import time
import sys
from typing import List, Dict, Optional, Set
import logging

# Configure logging - only show warnings and errors
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, max_pages: int = 50, delay: float = 0.5):
        self.max_pages = max_pages
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.visited_urls: Set[str] = set()
        
    def normalize_url(self, url: str) -> str:
        """
        Take a user input URL and return a normalized version.
        Example: "quill.co/blog/" -> "https://quill.co/blog"
        """
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse and reconstruct to normalize
        parsed = urlparse(url)
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path.rstrip('/') or '/',
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        return normalized

    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and internal to the base domain."""
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
            
            # Check if it's the same domain or subdomain
            return (parsed.netloc == base_domain or 
                   parsed.netloc.endswith('.' + base_domain))
        except:
            return False

    def extract_links(self, html: str, base_url: str, base_domain: str) -> List[str]:
        """Extract internal links from HTML content."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Clean up the URL
            full_url = self.normalize_url(full_url)
            
            if self.is_valid_url(full_url, base_domain):
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates

    def crawl_site(self, root_url: str) -> List[str]:
        """
        Starting from root_url, crawl for internal links.
        Returns: list of URLs to scrape
        """
        root_url = self.normalize_url(root_url)
        base_domain = urlparse(root_url).netloc
        
        urls_to_visit = [root_url]
        found_urls = set([root_url])
        
        logger.info(f"Starting crawl from {root_url}")
        
        while urls_to_visit and len(found_urls) < self.max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            try:
                logger.info(f"Crawling: {current_url}")
                response = self.session.get(current_url, timeout=10)
                response.raise_for_status()
                
                self.visited_urls.add(current_url)
                
                # Extract links from this page
                new_links = self.extract_links(response.text, current_url, base_domain)
                
                for link in new_links:
                    if link not in found_urls and len(found_urls) < self.max_pages:
                        found_urls.add(link)
                        urls_to_visit.append(link)
                
                # Be respectful to the server
                time.sleep(self.delay)
                
            except Exception as e:
                logger.warning(f"Failed to crawl {current_url}: {e}")
                continue
        
        logger.info(f"Found {len(found_urls)} URLs to scrape")
        return list(found_urls)

    def detect_content_type(self, url: str, title: str, content: str) -> str:
        """Detect content type based on URL patterns and content."""
        url_lower = url.lower()
        title_lower = title.lower() if title else ""
        
        # Check URL patterns
        if any(pattern in url_lower for pattern in ['/blog/', '/post/', '/article/']):
            return "blog"
        elif any(pattern in url_lower for pattern in ['/podcast/', '/episode/']):
            return "podcast_transcript"
        elif any(pattern in url_lower for pattern in ['/call/', '/meeting/']):
            return "call_transcript"
        elif any(pattern in url_lower for pattern in ['linkedin.com', '/posts/']):
            return "linkedin_post"
        elif any(pattern in url_lower for pattern in ['reddit.com', '/comments/']):
            return "reddit_comment"
        elif any(pattern in url_lower for pattern in ['/book/', '/books/']):
            return "book"
        elif any(pattern in url_lower for pattern in ['/guide/', '/guides/', '/tutorial/']):
            return "blog"  # Treat guides as blog content
        else:
            return "blog"  # Default to blog

    def extract_content(self, url: str) -> Optional[Dict]:
        """
        Extract clean article content from a URL.
        Returns dict with title, content, content_type, and source_url.
        """
        try:
            logger.info(f"Extracting content from: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Use trafilatura for content extraction
            extracted = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=True,
                include_images=False,
                include_links=True,
                output_format='markdown'
            )
            
            if not extracted:
                logger.warning(f"No content extracted from {url}")
                return None
            
            # Extract title using BeautifulSoup as fallback
            soup = BeautifulSoup(response.text, 'html.parser')
            title = None
            
            # Try multiple title extraction methods
            for selector in ['h1', 'title', '.post-title', '.entry-title', '.article-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # If no title found, try to extract from markdown
            if not title and extracted:
                lines = extracted.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
            
            # Fallback to URL-based title
            if not title:
                title = urlparse(url).path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            
            content_type = self.detect_content_type(url, title, extracted)
            
            return {
                "title": title,
                "content": extracted,
                "content_type": content_type,
                "source_url": url
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None

    def build_output(self, site_url: str, items: List[Dict]) -> Dict:
        """Build the final JSON output."""
        return {
            "site": site_url,
            "items": items
        }

    def scrape_site(self, url: str) -> Dict:
        """Main method to scrape a site and return JSON output."""
        normalized_url = self.normalize_url(url)
        
        # Step 1: Crawl for URLs
        urls = self.crawl_site(normalized_url)
        
        # Step 2: Extract content from each URL
        items = []
        for url_to_scrape in tqdm(urls, desc="Extracting content"):
            content_data = self.extract_content(url_to_scrape)
            if content_data:
                items.append(content_data)
            time.sleep(self.delay)  # Be respectful
        
        # Step 3: Build output
        output = self.build_output(normalized_url, items)
        
        logger.info(f"Successfully scraped {len(items)} items from {normalized_url}")
        return output

def test_coverage(urls: List[str]) -> None:
    """Test coverage on multiple sites."""
    scraper = WebScraper(max_pages=20)  # Smaller limit for testing
    
    for url in urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        try:
            result = scraper.scrape_site(url)
            total_items = len(result['items'])
            print(f"✅ Success: {total_items} items extracted")
            
            # Show sample items
            for i, item in enumerate(result['items'][:3]):
                print(f"  {i+1}. {item['title'][:60]}... ({item['content_type']})")
            
            if total_items > 3:
                print(f"  ... and {total_items - 3} more items")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <url> [output_file] [max_pages]")
        print("Example: python scraper.py https://quill.co/blog")
        print("Example: python scraper.py https://quill.co/blog quill_output.json")
        print("Example: python scraper.py https://quill.co/blog quill_output.json 100")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    # Generate output filename if not provided
    if not output_file:
        domain = urlparse(url).netloc.replace('www.', '').replace('.', '_')
        output_file = f"{domain}_scraped.json"
    
    scraper = WebScraper(max_pages=max_pages)
    
    try:
        print(f"🚀 Starting scrape of {url}")
        print(f"📄 Output will be saved to: {output_file}")
        print("⏳ This may take a few minutes...")
        
        result = scraper.scrape_site(url)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully scraped {len(result['items'])} items")
        print(f"📁 Results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
