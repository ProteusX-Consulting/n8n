#!/usr/bin/env python3
"""
Enhanced Web Crawler with Jina Integration + Image Extraction for N8N Website Workflow
=====================================================================================

This script integrates with your n8n Website Workflow:
1. Takes domain from previous n8n node
2. Finds the latest crawl overview JSON in local-files/seo-output/domain/
3. Extracts ALL addresses from the crawl data
4. Calls Jina API for each address (for text content)
5. Extracts images from each page (separate HTML request)
6. Optionally downloads images
7. Outputs consolidated JSON file with both text and image data

ENHANCED FEATURES:
- Comprehensive image detection (img tags, CSS backgrounds, JavaScript, data attributes)
- Multiple image source attributes (src, data-src, data-lazy-src, etc.)
- Selenium fallback for JavaScript-heavy sites
- Better error handling and download management
- Detailed debugging output

REQUIREMENTS:
pip install beautifulsoup4 requests selenium

Optional Selenium setup:
- Download ChromeDriver from https://chromedriver.chromium.org/
- Add to PATH or place in project directory

Usage:
python local-files/spiders/web_crawler.py rubinlicatesi.com
"""

import json
import requests
import time
import sys
import os
import glob
import re
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

def find_crawl_file(domain: str) -> str:
    """
    Find the most recent crawl overview file for the domain
    Runs from n8n root directory, looks in local-files/seo-output
    
    Args:
        domain: Domain name from n8n node (e.g., "rubinlicatesi.com")
        
    Returns:
        Path to the crawl file
    """
    # Convert domain to filename format (dots to underscores)
    domain_clean = domain.replace('.', '_')
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script running from: {script_dir}")
    
    # Possible base paths relative to n8n root directory
    possible_base_paths = [
        "local-files/seo-output",  # Direct relative path
        "./local-files/seo-output",  # Explicit current dir
        os.path.join(os.getcwd(), "local-files", "seo-output"),  # Using current working directory
    ]
    
    for base_path in possible_base_paths:
        # Convert to absolute path for clarity
        abs_base_path = os.path.abspath(base_path)
        search_pattern = os.path.join(abs_base_path, domain, f"{domain_clean}_crawl_overview_*.json")
        
        # Use forward slashes for glob even on Windows
        search_pattern = search_pattern.replace('\\', '/')
        files = glob.glob(search_pattern)
        
        print(f"Trying: {search_pattern}")
        
        if files:
            # Found files with this base path - use it
            latest_file = sorted(files, reverse=True)[0]
            print(f"Found crawl file: {latest_file}")
            return latest_file
    
    print(f"No crawl overview files found for domain: {domain}")
    return None

def extract_all_addresses(crawl_file: str) -> List[str]:
    """
    Extract ALL addresses from the crawl JSON file
    
    Args:
        crawl_file: Path to the crawl overview JSON file
        
    Returns:
        List of all unique URLs found in the crawl data
    """
    try:
        print(f"Reading crawl file: {crawl_file}")
        
        with open(crawl_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        addresses = []
        
        # Handle the standard crawl format: {"crawl_stats": {...}, "pages": [...]}
        if 'pages' in data and isinstance(data['pages'], list):
            print(f"Processing {len(data['pages'])} pages from crawl data")
            
            for page in data['pages']:
                if isinstance(page, dict) and 'address' in page:
                    addresses.append(page['address'])
        
        elif isinstance(data, list):
            # Handle direct list format
            print(f"Processing {len(data)} pages from direct list format")
            for page in data:
                if isinstance(page, dict) and 'address' in page:
                    addresses.append(page['address'])
        
        # Remove duplicates and sort
        unique_addresses = sorted(list(set(addresses)))
        print(f"Extracted {len(unique_addresses)} unique addresses from crawl data")
        
        return unique_addresses
        
    except Exception as e:
        print(f"Error extracting addresses from {crawl_file}: {e}")
        return []

def extract_images_from_page(url: str, base_url: str) -> List[Dict]:
    """
    Extract all images from a single page with comprehensive detection
    
    Args:
        url: URL to scrape for images
        base_url: Base URL for resolving relative image paths
        
    Returns:
        List of image dictionaries with URL, alt text, etc.
    """
    images = []
    found_urls = set()  # Prevent duplicates
    
    try:
        # Use comprehensive headers to mimic real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, timeout=20, headers=headers, allow_redirects=True)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"    HTML size: {len(response.content)} bytes")
            
            # 1. Find all IMG tags with comprehensive attribute checking
            img_tags = soup.find_all('img')
            print(f"    Found {len(img_tags)} <img> tags")
            
            for i, img in enumerate(img_tags):
                # Try ALL possible image source attributes
                possible_sources = [
                    'src', 'data-src', 'data-lazy-src', 'data-original', 
                    'data-srcset', 'data-lazy', 'data-original-src',
                    'data-echo', 'data-lazy-load', 'data-defer-src',
                    'data-image', 'data-img', 'data-url'
                ]
                
                img_src = None
                source_attr = None
                
                for attr in possible_sources:
                    if img.get(attr):
                        img_src = img.get(attr)
                        source_attr = attr
                        break
                
                if img_src:
                    # Handle srcset (take first URL)
                    if ',' in img_src:
                        img_src = img_src.split(',')[0].strip().split(' ')[0]
                    
                    # Convert relative URLs to absolute
                    img_url = urljoin(base_url, img_src)
                    
                    # Skip duplicates
                    if img_url in found_urls:
                        continue
                    found_urls.add(img_url)
                    
                    # Extract comprehensive image info
                    image_info = {
                        'src': img_url,
                        'original_src': img_src,
                        'source_attribute': source_attr,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', ''),
                        'class': ' '.join(img.get('class', [])) if img.get('class') else '',
                        'id': img.get('id', ''),
                        'loading': img.get('loading', ''),
                        'filename': os.path.basename(urlparse(img_url).path),
                        'page_url': url,
                        'img_tag_index': i
                    }
                    
                    images.append(image_info)
                    print(f"      IMG {i+1}: {img_url} (via {source_attr})")
                else:
                    print(f"      IMG {i+1}: No source found - attributes: {list(img.attrs.keys())}")
            
            # 2. Check PICTURE and SOURCE tags
            picture_tags = soup.find_all('picture')
            print(f"    Found {len(picture_tags)} <picture> tags")
            
            for picture in picture_tags:
                sources = picture.find_all('source')
                for source in sources:
                    srcset = source.get('srcset')
                    if srcset:
                        # Take first URL from srcset
                        img_src = srcset.split(',')[0].strip().split(' ')[0]
                        img_url = urljoin(base_url, img_src)
                        
                        if img_url not in found_urls:
                            found_urls.add(img_url)
                            image_info = {
                                'src': img_url,
                                'original_src': img_src,
                                'source_attribute': 'srcset',
                                'alt': 'Picture source',
                                'title': '',
                                'width': '',
                                'height': '',
                                'class': 'picture-source',
                                'id': '',
                                'loading': '',
                                'filename': os.path.basename(urlparse(img_url).path),
                                'page_url': url,
                                'img_tag_index': -1
                            }
                            images.append(image_info)
                            print(f"      PICTURE: {img_url}")
            
            # 3. Check for CSS background images in style attributes
            style_elements = soup.find_all(attrs={"style": True})
            print(f"    Found {len(style_elements)} elements with style attributes")
            
            bg_count = 0
            for element in style_elements:
                style = element.get('style', '')
                if 'background-image' in style:
                    import re
                    matches = re.findall(r'url\(["\']?(.*?)["\']?\)', style)
                    for match in matches:
                        img_url = urljoin(base_url, match)
                        
                        if img_url not in found_urls:
                            found_urls.add(img_url)
                            bg_count += 1
                            image_info = {
                                'src': img_url,
                                'original_src': match,
                                'source_attribute': 'style-background',
                                'alt': f'CSS background image {bg_count}',
                                'title': '',
                                'width': '',
                                'height': '',
                                'class': 'css-background',
                                'id': '',
                                'loading': '',
                                'filename': os.path.basename(urlparse(img_url).path),
                                'page_url': url,
                                'img_tag_index': -1
                            }
                            images.append(image_info)
                            print(f"      CSS BG: {img_url}")
            
            # 4. Look for images in JavaScript or data attributes
            script_tags = soup.find_all('script')
            print(f"    Checking {len(script_tags)} <script> tags for image URLs")
            
            js_count = 0
            for script in script_tags:
                if script.string:
                    # Look for image URLs in JavaScript
                    import re
                    # Match common image URL patterns
                    img_patterns = [
                        r'"(https?://[^"]*\.(?:jpg|jpeg|png|gif|webp|svg))"',
                        r"'(https?://[^']*\.(?:jpg|jpeg|png|gif|webp|svg))'",
                        r'"([^"]*\.(?:jpg|jpeg|png|gif|webp|svg))"',
                        r"'([^']*\.(?:jpg|jpeg|png|gif|webp|svg))'"
                    ]
                    
                    for pattern in img_patterns:
                        matches = re.findall(pattern, script.string, re.IGNORECASE)
                        for match in matches:
                            img_url = urljoin(base_url, match)
                            
                            if img_url not in found_urls and img_url.startswith('http'):
                                found_urls.add(img_url)
                                js_count += 1
                                image_info = {
                                    'src': img_url,
                                    'original_src': match,
                                    'source_attribute': 'javascript',
                                    'alt': f'JavaScript image {js_count}',
                                    'title': '',
                                    'width': '',
                                    'height': '',
                                    'class': 'javascript-image',
                                    'id': '',
                                    'loading': '',
                                    'filename': os.path.basename(urlparse(img_url).path),
                                    'page_url': url,
                                    'img_tag_index': -1
                                }
                                images.append(image_info)
                                print(f"      JS IMAGE: {img_url}")
            
            # 5. Check all elements for data attributes that might contain image URLs
            all_elements = soup.find_all()
            data_count = 0
            
            for element in all_elements:
                for attr_name, attr_value in element.attrs.items():
                    if attr_name.startswith('data-') and isinstance(attr_value, str):
                        # Check if this looks like an image URL
                        if any(ext in attr_value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                            img_url = urljoin(base_url, attr_value)
                            
                            if img_url not in found_urls and img_url.startswith('http'):
                                found_urls.add(img_url)
                                data_count += 1
                                image_info = {
                                    'src': img_url,
                                    'original_src': attr_value,
                                    'source_attribute': attr_name,
                                    'alt': f'Data attribute image {data_count}',
                                    'title': '',
                                    'width': '',
                                    'height': '',
                                    'class': f'data-{attr_name}',
                                    'id': '',
                                    'loading': '',
                                    'filename': os.path.basename(urlparse(img_url).path),
                                    'page_url': url,
                                    'img_tag_index': -1
                                }
                                images.append(image_info)
                                print(f"      DATA ATTR: {img_url} (from {attr_name})")
        
        else:
            print(f"    HTTP Error: {response.status_code}")
        
    except Exception as e:
        print(f"    Error extracting images from {url}: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"    TOTAL IMAGES FOUND: {len(images)}")
    return images

def extract_images_with_selenium(url: str, base_url: str) -> List[Dict]:
    """
    Alternative image extraction using Selenium for JavaScript-heavy sites
    Only use this if the regular extraction finds too few images
    
    Args:
        url: URL to scrape for images
        base_url: Base URL for resolving relative image paths
        
    Returns:
        List of image dictionaries
    """
    images = []
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Setup headless Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print(f"    Using Selenium to load: {url}")
        driver.get(url)
        
        # Wait for page to load and images to appear
        time.sleep(3)
        
        # Scroll to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Find all images after JavaScript execution
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        print(f"    Selenium found {len(img_elements)} img elements")
        
        found_urls = set()
        
        for i, img in enumerate(img_elements):
            try:
                # Get the final computed src after JavaScript
                img_src = img.get_attribute('src')
                
                if img_src and img_src not in found_urls:
                    found_urls.add(img_src)
                    
                    # Get all available attributes
                    image_info = {
                        'src': img_src,
                        'original_src': img_src,
                        'source_attribute': 'selenium-src',
                        'alt': img.get_attribute('alt') or '',
                        'title': img.get_attribute('title') or '',
                        'width': img.get_attribute('width') or '',
                        'height': img.get_attribute('height') or '',
                        'class': img.get_attribute('class') or '',
                        'id': img.get_attribute('id') or '',
                        'loading': img.get_attribute('loading') or '',
                        'filename': os.path.basename(urlparse(img_src).path),
                        'page_url': url,
                        'img_tag_index': i
                    }
                    
                    images.append(image_info)
                    print(f"      SELENIUM IMG {i+1}: {img_src}")
                    
            except Exception as e:
                print(f"      Error processing selenium image {i}: {e}")
        
        driver.quit()
        
    except ImportError:
        print("    Selenium not available. Install with: pip install selenium")
        return []
    except Exception as e:
        print(f"    Selenium error: {e}")
        return []
    
    print(f"    SELENIUM TOTAL: {len(images)} images")
    return images
    """
    Download a single image
    
    Args:
        image_info: Dictionary containing image information
        download_folder: Folder to save images
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        img_url = image_info['src']
        filename = image_info['filename']
        
        # Ensure we have a valid filename
        if not filename or '.' not in filename:
            ext = '.jpg'  # Default extension
            # Try to guess extension from URL
            parsed_url = urlparse(img_url)
            if '.' in parsed_url.path:
                ext = os.path.splitext(parsed_url.path)[1]
            filename = f"image_{hash(img_url)}{ext}"
        
        filepath = os.path.join(download_folder, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath):
            return True
        
        # Download the image
        response = requests.get(img_url, stream=True, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Update image_info with local path
            image_info['local_path'] = filepath
            image_info['file_size'] = os.path.getsize(filepath)
            return True
            
    except Exception as e:
        print(f"    Failed to download {image_info['src']}: {e}")
        image_info['download_error'] = str(e)
    
    return False

def call_jina_api(url: str, api_key: str) -> Dict:
    """
    Call Jina Reader API for a single URL
    
    Args:
        url: URL to scrape
        api_key: Jina API key
        
    Returns:
        Dictionary with scraped content
    """
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'text/plain'
    }
    
    result = {
        'address': url,
        'scraped_at': datetime.now().isoformat(),
        'success': False
    }
    
    try:
        response = requests.get(jina_url, headers=headers, timeout=25)
        
        if response.status_code == 200:
            content = response.text.strip()
            # Store content with actual newlines, not escaped ones
            content = content.replace('\\n', '\n')
            result.update({
                'success': True,
                'status_code': response.status_code,
                'content': content,
                'content_length': len(content),
                'word_count': len(content.split()) if content else 0,
                'jina_url': jina_url
            })
        else:
            result.update({
                'status_code': response.status_code,
                'error': f"HTTP {response.status_code}",
                'content': '',
                'jina_url': jina_url
            })
            
    except requests.exceptions.Timeout:
        result.update({
            'error': 'Request timeout (25s)',
            'content': '',
            'jina_url': jina_url
        })
    except Exception as e:
        result.update({
            'error': str(e),
            'content': '',
            'jina_url': jina_url
        })
    
    return result

def scrape_all_addresses(domain: str, addresses: List[str], api_key: str, download_images: bool = True) -> Dict:
    """
    Scrape all addresses using Jina API and extract images with multiple methods
    
    Args:
        domain: Domain name
        addresses: List of URLs to scrape
        api_key: Jina API key
        download_images: Whether to download images locally
        
    Returns:
        Dictionary with flat array of address/content pairs plus images
    """
    total_urls = len(addresses)
    successful = 0
    failed = 0
    total_images = 0
    
    print(f"Starting ENHANCED scraping for {total_urls} URLs from domain: {domain}")
    print(f"Image downloading: {'Enabled' if download_images else 'Disabled'}")
    
    # Create images directory if downloading
    images_dir = None
    if download_images:
        images_dir = os.path.join(os.getcwd(), "local-files", "web-output", domain, "images")
        os.makedirs(images_dir, exist_ok=True)
        print(f"Images will be saved to: {images_dir}")
    
    # Main results structure
    results = {
        'domain': domain,
        'scraping_metadata': {
            'total_urls': total_urls,
            'scraping_started': datetime.now().isoformat(),
            'jina_api_endpoint': 'https://r.jina.ai/',
            'source': 'enhanced_jina_scraper_v2',
            'integration': 'n8n_website_workflow',
            'image_extraction_enabled': True,
            'image_downloading_enabled': download_images,
            'selenium_available': False
        },
        'scraped_pages': []
    }
    
    # Check if Selenium is available
    try:
        import selenium
        results['scraping_metadata']['selenium_available'] = True
        print("Selenium is available for JavaScript-heavy sites")
    except ImportError:
        print("Selenium not available - only static HTML image extraction")
    
    base_url = f"https://{domain}"
    
    for i, url in enumerate(addresses, 1):
        print(f"\n[{i}/{total_urls}] Processing: {url}")
        
        # Call Jina API for text content
        print(f"  Getting text content via Jina...")
        jina_result = call_jina_api(url, api_key)
        
        # Extract images from page - try multiple methods
        print(f"  Extracting images with comprehensive detection...")
        page_images = extract_images_from_page(url, base_url)
        
        # If we found very few images, try Selenium (for JS-heavy sites)
        if len(page_images) <= 2 and results['scraping_metadata']['selenium_available']:
            print(f"  Only found {len(page_images)} images, trying Selenium...")
            selenium_images = extract_images_with_selenium(url, base_url)
            
            # Merge results, avoiding duplicates
            existing_srcs = {img['src'] for img in page_images}
            for sel_img in selenium_images:
                if sel_img['src'] not in existing_srcs:
                    page_images.append(sel_img)
            
            print(f"  Combined total: {len(page_images)} images")
        
        # Download images if enabled
        downloaded_count = 0
        download_errors = []
        
        if download_images and page_images:
            print(f"  Downloading {len(page_images)} images...")
            for img_idx, img in enumerate(page_images, 1):
                print(f"    [{img_idx}/{len(page_images)}] {img['filename']}")
                success = download_image(img, images_dir)
                if success:
                    downloaded_count += 1
                    print(f"      ✓ Downloaded")
                else:
                    error = img.get('download_error', 'Unknown error')
                    download_errors.append(f"{img['filename']}: {error}")
                    print(f"      ✗ Failed: {error}")
        
        # Create comprehensive page result
        page_result = {
            'address': url,
            'content': jina_result.get('content', ''),
            'scraped_at': jina_result['scraped_at'],
            'success': jina_result['success'],
            'content_length': jina_result.get('content_length', 0),
            'word_count': jina_result.get('word_count', 0),
            'images': {
                'total_found': len(page_images),
                'downloaded': downloaded_count,
                'download_errors': download_errors,
                'images_list': page_images
            }
        }
        
        # Add error info if failed
        if not jina_result['success']:
            page_result['error'] = jina_result.get('error', 'Unknown error')
            page_result['status_code'] = jina_result.get('status_code', 0)
        
        # Add to results array
        results['scraped_pages'].append(page_result)
        
        # Update counters
        if jina_result['success']:
            successful += 1
            chars = jina_result['content_length']
            words = jina_result['word_count']
            print(f"  ✓ Text: {chars} chars, {words} words")
        else:
            failed += 1
            error = jina_result.get('error', 'Unknown error')
            print(f"  ✗ Text: {error}")
        
        total_images += len(page_images)
        print(f"  📷 Images: Found {len(page_images)}, Downloaded {downloaded_count}")
        
        if download_errors:
            print(f"  ⚠ Download errors: {len(download_errors)}")
        
        # Rate limiting
        if i < total_urls:
            time.sleep(0.5)
    
    # Update final metadata
    results['scraping_metadata'].update({
        'scraping_completed': datetime.now().isoformat(),
        'successful_scrapes': successful,
        'failed_scrapes': failed,
        'success_rate_percent': round((successful / total_urls * 100), 2) if total_urls > 0 else 0,
        'total_images_found': total_images,
        'images_directory': images_dir if download_images else None
    })
    
    print(f"\n" + "="*50)
    print(f"ENHANCED SCRAPING COMPLETED:")
    print(f"   Text - Successful: {successful}, Failed: {failed}")
    print(f"   Success Rate: {results['scraping_metadata']['success_rate_percent']}%")
    print(f"   Total Images Found: {total_images}")
    if download_images:
        total_downloaded = sum(page['images']['downloaded'] for page in results['scraped_pages'])
        total_errors = sum(len(page['images']['download_errors']) for page in results['scraped_pages'])
        print(f"   Total Images Downloaded: {total_downloaded}")
        print(f"   Download Errors: {total_errors}")
    print("="*50)
    
    return results

def save_results(domain: str, results: Dict) -> str:
    """
    Save results to the web-output directory
    
    Args:
        domain: Domain name
        results: Complete results dictionary
        
    Returns:
        Path to saved file
    """
    # Try multiple possible output paths from n8n root directory
    possible_output_paths = [
        "local-files/web-output",
        "./local-files/web-output",
        os.path.join(os.getcwd(), "local-files", "web-output"),
    ]
    
    output_dir = None
    for base_path in possible_output_paths:
        try:
            abs_base_path = os.path.abspath(base_path)
            test_dir = os.path.join(abs_base_path, domain)
            os.makedirs(test_dir, exist_ok=True)
            output_dir = test_dir
            print(f"Using output directory: {output_dir}")
            break
        except Exception as e:
            print(f"Cannot create directory {abs_base_path}/{domain}: {e}")
            continue
    
    if not output_dir:
        raise Exception("Cannot create output directory in any of the tried locations")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON file with text content and image metadata
    json_output_file = os.path.join(output_dir, f"{domain}_enhanced_scraped_content_{timestamp}.json")
    
    # Save individual text files
    text_files_dir = os.path.join(output_dir, f"text_files_{timestamp}")
    os.makedirs(text_files_dir, exist_ok=True)
    
    # Save image metadata as separate JSON
    images_json_file = os.path.join(output_dir, f"{domain}_images_metadata_{timestamp}.json")
    
    try:
        # Save main JSON file
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save individual text files for each page
        for i, page in enumerate(results['scraped_pages'], 1):
            if page.get('success') and page.get('content'):
                url = page['address']
                safe_filename = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('?', '_').replace('&', '_')
                if safe_filename.endswith('_'):
                    safe_filename = safe_filename[:-1]
                if not safe_filename:
                    safe_filename = f"page_{i}"
                
                text_file_path = os.path.join(text_files_dir, f"{safe_filename}.txt")
                
                with open(text_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {page['address']}\n")
                    f.write(f"Scraped at: {page['scraped_at']}\n")
                    f.write(f"Content length: {page['content_length']}\n")
                    f.write(f"Word count: {page['word_count']}\n")
                    f.write(f"Images found: {page['images']['total_found']}\n")
                    f.write(f"Images downloaded: {page['images']['downloaded']}\n")
                    f.write("-" * 80 + "\n\n")
                    f.write(page['content'])
        
        # Save images metadata separately
        images_data = {
            'domain': domain,
            'extraction_date': datetime.now().isoformat(),
            'total_pages': len(results['scraped_pages']),
            'total_images': sum(page['images']['total_found'] for page in results['scraped_pages']),
            'images_by_page': [
                {
                    'page_url': page['address'],
                    'images_found': page['images']['total_found'],
                    'images_downloaded': page['images']['downloaded'],
                    'images': page['images']['images_list']
                }
                for page in results['scraped_pages']
                if page['images']['total_found'] > 0
            ]
        }
        
        with open(images_json_file, 'w', encoding='utf-8') as f:
            json.dump(images_data, f, indent=2, ensure_ascii=False)
        
        print(f"Enhanced results saved:")
        print(f"  Main JSON: {json_output_file}")
        print(f"  Images metadata: {images_json_file}")
        print(f"  Text files: {text_files_dir}")
        print(f"  Images folder: {results['scraping_metadata'].get('images_directory', 'N/A')}")
        
        return json_output_file
        
    except Exception as e:
        print(f"Error saving results: {e}")
        raise

def main():
    """Main function for n8n execution"""
    
    # Jina API Key - get from environment variable
    JINA_API_KEY = os.getenv('JINA_API_KEY')
    if not JINA_API_KEY:
        print("Error: JINA_API_KEY environment variable not set")
        print("Please set your Jina API key as an environment variable:")
        print("export JINA_API_KEY='your_jina_api_key_here'")
        sys.exit(1)
    
    # Configuration
    DOWNLOAD_IMAGES = True  # Set to False to only extract image metadata without downloading
    
    # Get domain from n8n or command line
    if len(sys.argv) != 2:
        print("Usage: python3 web_crawler.py <domain>")
        print("   Example: python3 web_crawler.py rubinlicatesi.com")
        print("   Note: This script is designed for n8n workflow integration")
        sys.exit(1)
    
    domain = sys.argv[1].strip()
    print(f"Domain received: {domain}")
    
    try:
        # Step 1: Find and read the original crawl data
        print(f"Looking for crawl data...")
        crawl_file = find_crawl_file(domain)
        
        if not crawl_file:
            print(f"No crawl data found for domain: {domain}")
            sys.exit(1)
        
        # Step 2: Extract ALL addresses from the original crawl file
        print(f"Extracting all addresses from original crawl data...")
        addresses = extract_all_addresses(crawl_file)
        
        if not addresses:
            print(f"No addresses found in crawl file: {crawl_file}")
            sys.exit(1)
        
        print(f"Found {len(addresses)} addresses in original crawl data")
        
        # Step 3: Enhanced scraping with both text and images
        print(f"Starting enhanced scraping (text + images)...")
        enhanced_results = scrape_all_addresses(domain, addresses, JINA_API_KEY, DOWNLOAD_IMAGES)
        
        # Step 4: Save comprehensive results
        output_file = save_results(domain, enhanced_results)
        
        print(f"\nSUCCESS! Enhanced scraping completed for {domain}")
        print(f"Output file: {output_file}")
        print(f"Pages processed: {len(enhanced_results['scraped_pages'])}")
        print(f"Text success rate: {enhanced_results['scraping_metadata']['success_rate_percent']}%")
        print(f"Total images found: {enhanced_results['scraping_metadata']['total_images_found']}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()