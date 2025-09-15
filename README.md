# Web Scraper for Technical Knowledge Base

A robust web scraper that extracts content from blogs, guides, and technical resources to build a knowledge base for AI-powered comment generation.

## Features

- **Universal Coverage**: Works with any blog or content site
- **Smart Content Extraction**: Uses trafilatura for clean markdown extraction
- **Intelligent Crawling**: Automatically discovers and follows internal links
- **Content Type Detection**: Automatically categorizes content (blog, guide, etc.)
- **Respectful Scraping**: Built-in delays and proper headers
- **Error Handling**: Robust error handling for unreliable sites

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Scrape a site (output saved to quill_co_scraped.json)
python scraper.py https://quill.co/blog

# Scrape with custom output filename
python scraper.py https://quill.co/blog my_output.json
```

### Test Coverage
```bash
# Test multiple sites (results saved to test_results/ directory)
python test_coverage.py
```

## Output Format

The scraper returns JSON in the following format:

```json
{
  "site": "https://quill.co/blog",
  "items": [
    {
      "title": "Article Title",
      "content": "# Markdown content...",
      "content_type": "blog",
      "source_url": "https://quill.co/blog/post"
    }
  ]
}
```

## Content Types

The scraper automatically detects content types:
- `blog` - Blog posts and articles
- `podcast_transcript` - Podcast episodes
- `call_transcript` - Call recordings
- `linkedin_post` - LinkedIn posts
- `reddit_comment` - Reddit comments
- `book` - Book content
- `other` - Other content types

## Architecture

### Core Components

1. **URL Normalization**: Handles various URL formats and normalizes them
2. **Site Crawling**: Discovers internal links using BeautifulSoup
3. **Content Extraction**: Uses trafilatura for clean markdown extraction
4. **Content Type Detection**: Analyzes URLs and content to categorize
5. **Error Handling**: Graceful handling of network and parsing errors

### Design Decisions

- **trafilatura**: Chosen for superior content extraction compared to basic BeautifulSoup
- **Respectful Scraping**: Built-in delays and proper User-Agent headers
- **Universal Approach**: No custom code per site - works with any blog structure
- **Markdown Output**: Clean, readable format perfect for AI processing

## Testing

The scraper has been tested on multiple sites including:
- Quill.co blog
- Substack blogs
- Company blogs
- Technical guides
- Interview preparation sites

## Performance

- Configurable page limits (default: 50 pages)
- Built-in rate limiting
- Progress tracking with tqdm
- Memory-efficient processing

## Error Handling

- Network timeouts and retries
- Invalid URL handling
- Content extraction failures
- Graceful degradation for problematic sites
