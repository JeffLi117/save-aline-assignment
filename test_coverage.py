#!/usr/bin/env python3
"""
Coverage Testing Script
=======================
Test the scraper on multiple sites to verify coverage and functionality.
Results are saved to individual files and a summary report.
"""

import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import WebScraper

# Test sites from the challenge + additional test blogs
TEST_SITES = [
    # Original challenge sites
    "https://quill.co/blog",
    "https://shreycation.substack.com",
    "https://lioness.io",
    "https://resilio.com",
    "https://biconnector.com",
    "https://www.thebluedot.co",
    "https://www.assorthealth.com",
    "https://franchiseki.com",
    "https://interviewing.io/blog",
    "https://nilmamano.com/blog/category/dsa",
    
    # Additional test blogs for better coverage
    "https://tech.nextroll.com/blog/",
    "https://blog.booking.com/",
    "https://medium.com/justeattakeaway-tech",
    "https://blog.khanacademy.org/engineering/",
    "https://developer.okta.com/blog/",
    "https://shopify.engineering/",
]

def test_coverage_with_files(urls):
    """Test coverage on multiple sites and save results to files."""
    # Use different limits based on site type
    scraper = WebScraper(max_pages=30)  # Balanced limit for testing
    results = []
    
    # Create output directory
    output_dir = "test_results"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🧪 Testing Web Scraper Coverage")
    print("=" * 60)
    print(f"Testing {len(urls)} sites...")
    print(f"📁 Results will be saved to: {output_dir}/")
    print("=" * 60)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Testing: {url}")
        print("-" * 40)
        
        try:
            result = scraper.scrape_site(url)
            total_items = len(result['items'])
            
            # Save individual result
            domain = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.', '_')
            filename = f"{output_dir}/{domain}_result.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Record summary
            test_result = {
                "url": url,
                "status": "success",
                "items_found": total_items,
                "output_file": filename,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Success: {total_items} items extracted")
            print(f"📄 Saved to: {filename}")
            
            # Show sample items
            for j, item in enumerate(result['items'][:2]):
                print(f"  • {item['title'][:50]}... ({item['content_type']})")
            
            if total_items > 2:
                print(f"  ... and {total_items - 2} more items")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            test_result = {
                "url": url,
                "status": "failed",
                "error": str(e),
                "items_found": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        results.append(test_result)
    
    # Save summary report
    summary = {
        "test_timestamp": datetime.now().isoformat(),
        "total_sites": len(urls),
        "successful_sites": len([r for r in results if r['status'] == 'success']),
        "total_items": sum(r.get('items_found', 0) for r in results),
        "results": results
    }
    
    summary_file = f"{output_dir}/coverage_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 COVERAGE TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful sites: {summary['successful_sites']}/{summary['total_sites']}")
    print(f"📄 Total items scraped: {summary['total_items']}")
    print(f"📁 Summary saved to: {summary_file}")
    print("=" * 60)
    
    return summary

if __name__ == "__main__":
    test_coverage_with_files(TEST_SITES)
