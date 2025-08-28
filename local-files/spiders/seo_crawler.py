import scrapy
import json
import re
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
import time
from datetime import datetime
import os


class SEOCrawlSpider(CrawlSpider):
    """
    Enhanced comprehensive SEO crawler that replicates Screaming Frog functionality.
    Improved for better page discovery and coverage matching BeamUsUp results.
    """
    
    name = 'seo_crawler'
    
    # Enhanced custom settings for better coverage
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 0.5,  # Reduced delay for faster crawling
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 32,  # Increased for faster crawling
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,  # Increased
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 3,  # Reduced max delay
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4.0,  # Increased concurrency
        'USER_AGENT': 'SEOBot/1.0 (+http://www.example.com/bot)',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',
        'DEPTH_LIMIT': 15,  # Increased from 10
        'CLOSESPIDER_PAGECOUNT': 10000,  # Keep your original higher limit
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],  # Retry on rate limits
        'DOWNLOAD_TIMEOUT': 30,
        'COOKIES_ENABLED': True,
    }
    
    def __init__(self, domain=None, output_format='json', output_dir=None, *args, **kwargs):
        super(SEOCrawlSpider, self).__init__(*args, **kwargs)
        
        if not domain:
            raise ValueError("Domain parameter is required")
        
        self.domain = domain.replace('http://', '').replace('https://', '').strip('/')
        
        # Try multiple URL variations for better coverage
        self.start_urls = [
            f'https://{self.domain}',
            f'https://www.{self.domain}',
            f'http://{self.domain}',
            f'http://www.{self.domain}',
        ]
        
        # Allow both www and non-www versions
        self.allowed_domains = [self.domain, f'www.{self.domain}']
        self.output_format = output_format.lower()
        
        # Set output directory (default to /files/crawl-output if not provided)
        self.output_dir = output_dir or '/files/crawl-output'
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize data storage
        self.crawl_data = []
        self.sitemap_urls = set()  # Track sitemap discovered URLs
        self.crawl_stats = {
            'start_time': datetime.now().isoformat(),
            'domain': self.domain,
            'total_pages': 0,
            'errors': 0,
            'redirects': 0,
            'sitemap_urls_found': 0
        }
        
        # Enhanced link extractor with better patterns
        self.link_extractor = LinkExtractor(
            allow_domains=[self.domain, f'www.{self.domain}'],
            deny_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 
                           'jpg', 'jpeg', 'png', 'gif', 'svg', 'ico', 'webp', 'mp4', 'avi', 
                           'mov', 'mp3', 'wav', 'css', 'js'],
            canonicalize=True,
            unique=True,
            # Deny problematic URLs
            deny=(
                r'.*\#.*',  # Deny fragment URLs
                r'.*\?.*utm_.*',  # Deny UTM tracking URLs
                r'.*\?.*fb.*',  # Deny Facebook tracking
                r'.*wp-admin.*',  # Deny WordPress admin
                r'.*wp-login.*',  # Deny WordPress login
                r'.*\.json$',  # Deny JSON files
                r'.*\.xml$',  # Deny XML files (except sitemaps)
                r'.*\.txt$',  # Deny text files
            ),
            # Process links to clean them
            process_value=lambda x: x.split('#')[0]  # Remove fragments
        )
        
        # Define crawling rules
        self.rules = (
            Rule(
                self.link_extractor,
                callback='parse_page',
                follow=True,
                process_request='process_request'
            ),
        )
        
        super(SEOCrawlSpider, self).__init__()
    
    def process_request(self, request, spider):
        """Add custom headers and processing to requests"""
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        request.headers['Accept-Language'] = 'en-US,en;q=0.5'
        request.headers['Accept-Encoding'] = 'gzip, deflate'
        request.headers['Cache-Control'] = 'no-cache'
        request.headers['DNT'] = '1'
        return request
    
    def start_requests(self):
        """Generate initial requests including sitemap discovery"""
        
        # First, try to get sitemaps and robots.txt
        discovery_urls = [
            f'https://{self.domain}/sitemap.xml',
            f'https://{self.domain}/sitemap_index.xml',
            f'https://{self.domain}/robots.txt',
            f'https://www.{self.domain}/sitemap.xml',
            f'https://www.{self.domain}/sitemap_index.xml',
            f'https://www.{self.domain}/robots.txt',
        ]
        
        for url in discovery_urls:
            yield Request(
                url,
                callback=self.parse_sitemap,
                meta={'handle_httpstatus_list': [404, 403, 500, 503], 'dont_redirect': True},
                dont_filter=True,
                priority=10  # High priority for discovery
            )
        
        # Then start normal crawling from home pages
        for url in self.start_urls:
            yield Request(
                url,
                callback=self.parse_page,
                meta={'depth': 0, 'is_start_url': True},
                dont_filter=True,
                priority=5
            )
    
    def parse_sitemap(self, response):
        """Parse sitemap or robots.txt to find more URLs"""
        if response.status == 200:
            if 'robots.txt' in response.url:
                # Look for sitemap references in robots.txt
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        if sitemap_url not in self.sitemap_urls:
                            self.sitemap_urls.add(sitemap_url)
                            yield Request(
                                sitemap_url, 
                                callback=self.parse_sitemap,
                                meta={'handle_httpstatus_list': [404, 403]},
                                dont_filter=True
                            )
            
            elif 'xml' in response.url and response.headers.get('Content-Type', b'').decode().startswith('text/xml'):
                # Parse XML sitemap
                try:
                    root = ET.fromstring(response.body)
                    
                    # Handle namespace
                    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    if root.tag.startswith('{'):
                        # Extract namespace
                        namespace = root.tag[1:].split('}')[0]
                        namespaces['ns'] = namespace
                    
                    # Handle sitemap index files
                    sitemaps = root.findall('.//ns:sitemap/ns:loc', namespaces) or root.findall('.//sitemap/loc')
                    for sitemap in sitemaps:
                        if sitemap.text and sitemap.text not in self.sitemap_urls:
                            self.sitemap_urls.add(sitemap.text)
                            yield Request(
                                sitemap.text, 
                                callback=self.parse_sitemap,
                                meta={'handle_httpstatus_list': [404, 403]},
                                dont_filter=True
                            )
                    
                    # Handle regular sitemap URLs
                    urls = root.findall('.//ns:url/ns:loc', namespaces) or root.findall('.//url/loc')
                    for url_elem in urls:
                        if url_elem.text:
                            url = url_elem.text.strip()
                            if self.is_allowed_url(url):
                                self.crawl_stats['sitemap_urls_found'] += 1
                                yield Request(
                                    url, 
                                    callback=self.parse_page,
                                    meta={'from_sitemap': True},
                                    priority=7
                                )
                
                except ET.ParseError as e:
                    self.logger.warning(f"Failed to parse XML sitemap {response.url}: {e}")
                except Exception as e:
                    self.logger.warning(f"Error processing sitemap {response.url}: {e}")
    
    def is_allowed_url(self, url):
        """Check if URL is allowed for crawling"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc == self.domain or 
                   parsed.netloc == f'www.{self.domain}' or
                   parsed.netloc.endswith(f'.{self.domain}'))
        except:
            return False
    
    def parse_page(self, response):
        """Main parsing method that extracts all SEO data"""
        
        # Basic page information
        page_data = {
            'address': response.url,
            'status_code': response.status,
            'status': self.get_status_text(response.status),
            'indexability': self.check_indexability(response),
            'indexability_status': self.get_indexability_status(response),
            'content_type': response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore'),
            'size_bytes': len(response.body),
            'response_time': response.meta.get('download_latency', 0) * 1000,  # Convert to ms
            'crawl_depth': response.meta.get('depth', 0),
            'last_modified': response.headers.get('Last-Modified', b'').decode('utf-8', errors='ignore'),
            'redirect_url': getattr(response, 'meta', {}).get('redirect_urls', [''])[-1] if getattr(response, 'meta', {}).get('redirect_urls') else '',
            'from_sitemap': response.meta.get('from_sitemap', False),
        }
        
        # Extract HTML content analysis
        if response.status == 200 and 'text/html' in page_data['content_type']:
            # Title analysis
            title_elements = response.css('title::text').getall()
            page_data['title_1'] = title_elements[0].strip() if title_elements else ''
            page_data['title_1_length'] = len(page_data['title_1'])
            page_data['title_1_pixel_width'] = self.estimate_pixel_width(page_data['title_1'])
            
            # Meta description
            meta_desc = response.css('meta[name="description"]::attr(content)').get()
            page_data['meta_description_1'] = (meta_desc or '').strip()
            page_data['meta_description_1_length'] = len(page_data['meta_description_1'])
            page_data['meta_description_1_pixel_width'] = self.estimate_pixel_width(page_data['meta_description_1'])
            
            # Meta keywords
            meta_keywords = response.css('meta[name="keywords"]::attr(content)').get()
            page_data['meta_keywords_1'] = (meta_keywords or '').strip()
            page_data['meta_keywords_1_length'] = len(page_data['meta_keywords_1'])
            
            # Heading analysis
            h1_elements = response.css('h1::text').getall()
            page_data['h1_1'] = h1_elements[0].strip() if h1_elements else ''
            page_data['h1_1_length'] = len(page_data['h1_1'])
            page_data['h1_count'] = len(h1_elements)
            
            page_data['h2_count'] = len(response.css('h2').getall())
            page_data['h3_count'] = len(response.css('h3').getall())
            page_data['h4_count'] = len(response.css('h4').getall())
            page_data['h5_count'] = len(response.css('h5').getall())
            page_data['h6_count'] = len(response.css('h6').getall())
            
            # Canonical analysis
            canonical = response.css('link[rel="canonical"]::attr(href)').get()
            page_data['canonical_link_element_1'] = urljoin(response.url, canonical) if canonical else ''
            
            # Robots meta tag
            robots_meta = response.css('meta[name="robots"]::attr(content)').get()
            page_data['meta_robots_1'] = (robots_meta or '').strip()
            
            # Open Graph and Twitter Card data
            page_data['og_title'] = response.css('meta[property="og:title"]::attr(content)').get() or ''
            page_data['og_description'] = response.css('meta[property="og:description"]::attr(content)').get() or ''
            page_data['og_image'] = response.css('meta[property="og:image"]::attr(content)').get() or ''
            page_data['twitter_title'] = response.css('meta[name="twitter:title"]::attr(content)').get() or ''
            page_data['twitter_description'] = response.css('meta[name="twitter:description"]::attr(content)').get() or ''
            
            # Content analysis - improved text extraction
            text_content = ' '.join(response.css('body *::text').getall())
            # Clean whitespace and count words
            clean_text = re.sub(r'\s+', ' ', text_content).strip()
            page_data['word_count'] = len(re.findall(r'\b\w+\b', clean_text))
            
            # Enhanced link analysis
            internal_links = self.extract_internal_links(response)
            external_links = self.extract_external_links(response)
            
            page_data['unique_inlinks'] = 0  # This would require a second pass
            page_data['unique_outlinks'] = len(set(external_links))
            page_data['internal_links_count'] = len(internal_links)
            page_data['external_links_count'] = len(external_links)
            
            # Image analysis
            images = response.css('img')
            page_data['images_count'] = len(images)
            page_data['images_without_alt_text'] = len([img for img in images if not img.css('::attr(alt)').get()])
            
            # Schema.org structured data
            structured_data = self.extract_structured_data(response)
            page_data['structured_data_count'] = len(structured_data)
            page_data['structured_data'] = json.dumps(structured_data) if structured_data else ''
            
            # Hreflang analysis
            hreflang_links = response.css('link[rel="alternate"][hreflang]')
            page_data['hreflang_count'] = len(hreflang_links)
            
            # Performance hints
            page_data['has_viewport_meta'] = bool(response.css('meta[name="viewport"]'))
            page_data['has_charset_meta'] = bool(response.css('meta[charset]') or response.css('meta[http-equiv="Content-Type"]'))
            
            # Additional SEO elements
            page_data['meta_robots_noindex'] = 'noindex' in page_data['meta_robots_1'].lower()
            page_data['meta_robots_nofollow'] = 'nofollow' in page_data['meta_robots_1'].lower()
            
        else:
            # Non-HTML or error pages - set default values
            self.set_default_values(page_data)
        
        # Update crawl statistics
        self.crawl_stats['total_pages'] += 1
        if response.status >= 400:
            self.crawl_stats['errors'] += 1
        if response.status in [301, 302, 303, 307, 308]:
            self.crawl_stats['redirects'] += 1
        
        # Store the data
        self.crawl_data.append(page_data)
        
        # Continue crawling by following links
        if response.status == 200 and 'text/html' in page_data.get('content_type', ''):
            links = self.link_extractor.extract_links(response)
            for link in links:
                yield Request(
                    link.url,
                    callback=self.parse_page,
                    meta={'depth': response.meta.get('depth', 0) + 1}
                )
    
    def extract_internal_links(self, response):
        """Extract all internal links including pagination and special patterns"""
        links = []
        
        # Regular links
        for link in response.css('a[href]'):
            href = link.css('::attr(href)').get()
            if href:
                absolute_url = urljoin(response.url, href)
                if self.is_allowed_url(absolute_url):
                    links.append(absolute_url)
        
        # Look for pagination links specifically
        pagination_selectors = [
            'a[rel="next"]',
            'a[rel="prev"]',
            'a.next',
            'a.previous',
            'a.page-numbers',
            '.pagination a',
            '.pager a',
            '.page-links a',
            'a[href*="page/"]',
            'a[href*="/p/"]',
            'a[href*="?page="]',
            'a[href*="&page="]',
        ]
        
        for selector in pagination_selectors:
            for link in response.css(selector):
                href = link.css('::attr(href)').get()
                if href:
                    absolute_url = urljoin(response.url, href)
                    if self.is_allowed_url(absolute_url):
                        links.append(absolute_url)
        
        # Look for WordPress/CMS specific patterns
        cms_selectors = [
            'a[href*="/category/"]',
            'a[href*="/tag/"]',
            'a[href*="/archive/"]',
            'a[href*="/author/"]',
            'a[href*="/date/"]',
        ]
        
        for selector in cms_selectors:
            for link in response.css(selector):
                href = link.css('::attr(href)').get()
                if href:
                    absolute_url = urljoin(response.url, href)
                    if self.is_allowed_url(absolute_url):
                        links.append(absolute_url)
        
        return list(set(links))  # Remove duplicates
    
    def extract_external_links(self, response):
        """Extract all external links from the page"""
        links = []
        for link in response.css('a[href]'):
            href = link.css('::attr(href)').get()
            if href and not href.startswith('#') and not href.startswith('mailto:') and not href.startswith('tel:'):
                absolute_url = urljoin(response.url, href)
                parsed = urlparse(absolute_url)
                if (parsed.netloc and 
                    parsed.netloc != self.domain and 
                    parsed.netloc != f'www.{self.domain}' and
                    not parsed.netloc.endswith(f'.{self.domain}')):
                    links.append(absolute_url)
        return links
    
    def extract_structured_data(self, response):
        """Extract JSON-LD and microdata structured data"""
        structured_data = []
        
        # JSON-LD
        json_ld_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in json_ld_scripts:
            try:
                data = json.loads(script.strip())
                structured_data.append(data)
            except json.JSONDecodeError:
                continue
        
        return structured_data
    
    def check_indexability(self, response):
        """Determine if page is indexable"""
        # Check robots meta tag
        robots_meta = response.css('meta[name="robots"]::attr(content)').get()
        if robots_meta:
            robots_directives = [directive.strip().lower() for directive in robots_meta.split(',')]
            if 'noindex' in robots_directives:
                return 'Non-Indexable'
        
        # Check status code
        if response.status != 200:
            return 'Non-Indexable'
        
        # Check content type
        content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore')
        if 'text/html' not in content_type:
            return 'Non-Indexable'
        
        return 'Indexable'
    
    def get_indexability_status(self, response):
        """Get detailed indexability status"""
        robots_meta = response.css('meta[name="robots"]::attr(content)').get()
        if robots_meta and 'noindex' in robots_meta.lower():
            return 'Noindex'
        
        if response.status != 200:
            return f'HTTP {response.status}'
        
        return 'Indexable'
    
    def get_status_text(self, status_code):
        """Convert status code to text"""
        status_texts = {
            200: 'OK',
            301: 'Moved Permanently',
            302: 'Found',
            303: 'See Other',
            304: 'Not Modified',
            307: 'Temporary Redirect',
            308: 'Permanent Redirect',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            410: 'Gone',
            429: 'Too Many Requests',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
            504: 'Gateway Timeout',
        }
        return status_texts.get(status_code, f'HTTP {status_code}')
    
    def estimate_pixel_width(self, text):
        """Rough estimation of pixel width for title/meta description"""
        if not text:
            return 0
        # Rough approximation: average character width of 8 pixels
        return len(text) * 8
    
    def set_default_values(self, page_data):
        """Set default values for non-HTML pages"""
        defaults = {
            'title_1': '', 'title_1_length': 0, 'title_1_pixel_width': 0,
            'meta_description_1': '', 'meta_description_1_length': 0, 'meta_description_1_pixel_width': 0,
            'meta_keywords_1': '', 'meta_keywords_1_length': 0,
            'h1_1': '', 'h1_1_length': 0, 'h1_count': 0,
            'h2_count': 0, 'h3_count': 0, 'h4_count': 0, 'h5_count': 0, 'h6_count': 0,
            'canonical_link_element_1': '', 'meta_robots_1': '',
            'og_title': '', 'og_description': '', 'og_image': '',
            'twitter_title': '', 'twitter_description': '',
            'word_count': 0, 'unique_inlinks': 0, 'unique_outlinks': 0,
            'internal_links_count': 0, 'external_links_count': 0,
            'images_count': 0, 'images_without_alt_text': 0,
            'structured_data_count': 0, 'structured_data': '',
            'hreflang_count': 0, 'has_viewport_meta': False, 'has_charset_meta': False,
            'meta_robots_noindex': False, 'meta_robots_nofollow': False, 'from_sitemap': False
        }
        page_data.update(defaults)
    
    def closed(self, reason):
        """Called when spider closes - save the results"""
        self.crawl_stats['end_time'] = datetime.now().isoformat()
        self.crawl_stats['reason'] = reason
        
        # Clean domain name for file paths
        domain_clean = self.domain.replace('.', '_')
        
        # Prepare final output
        output_data = {
            'crawl_stats': self.crawl_stats,
            'pages': self.crawl_data
        }
        
        # Save main output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.output_format == 'json':
            output_file = f'{self.output_dir}/{domain_clean}_crawl_overview_{timestamp}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        elif self.output_format == 'csv':
            output_file = f'{self.output_dir}/{domain_clean}_crawl_overview_{timestamp}.csv'
            if self.crawl_data:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.crawl_data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.crawl_data)
        
        # Create simple summary file that n8n workflow expects
        simple_output_file = f'{self.output_dir}/{domain_clean}_simple.json'
        simple_summary = {
            'domain': self.domain,
            'total_pages': len(self.crawl_data),
            'crawl_completed': len(self.crawl_data) > 0,  # True if any pages were crawled
            'output_file': output_file,
            'output_directory': self.output_dir,
            'timestamp': self.crawl_stats['end_time'],
            'errors': self.crawl_stats['errors'],
            'redirects': self.crawl_stats['redirects'],
            'sitemap_urls_found': self.crawl_stats['sitemap_urls_found'],
            'crawl_reason': reason
        }
        
        with open(simple_output_file, 'w', encoding='utf-8') as f:
            json.dump(simple_summary, f, indent=2)
        
        self.logger.info(f"Enhanced crawl completed. {len(self.crawl_data)} pages processed.")
        self.logger.info(f"Found {self.crawl_stats['sitemap_urls_found']} URLs from sitemaps.")
        self.logger.info(f"Main output saved to: {output_file}")
        self.logger.info(f"Summary saved to: {simple_output_file}")


# Enhanced Scrapy settings
SCRAPY_SETTINGS = {
    'BOT_NAME': 'seo_crawler',
    'SPIDER_MODULES': ['__main__'],
    'NEWSPIDER_MODULE': '__main__',
    'ROBOTSTXT_OBEY': True,
    'DOWNLOAD_DELAY': 0.5,
    'RANDOMIZE_DOWNLOAD_DELAY': True,
    'CONCURRENT_REQUESTS': 32,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
    'COOKIES_ENABLED': True,
    'TELNETCONSOLE_ENABLED': False,
    'DEFAULT_REQUEST_HEADERS': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'SEOBot/1.0 (+http://www.example.com/bot)',
        'DNT': '1',
    },
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 0.5,
    'AUTOTHROTTLE_MAX_DELAY': 3,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 4.0,
    'LOG_LEVEL': 'INFO',
    'RETRY_TIMES': 3,
    'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
    'DOWNLOAD_TIMEOUT': 30,
    'DEPTH_LIMIT': 15,
    'CLOSESPIDER_PAGECOUNT': 10000,
}


if __name__ == '__main__':
    # Command line execution
    import sys
    import os
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    if len(sys.argv) < 2:
        print("Usage: python seo_crawler.py <domain> [output_format] [output_directory]")
        print("Example: python seo_crawler.py nationalactionnetwork.net json /files/seo-output/nationalactionnetwork.net")
        sys.exit(1)
    
    domain = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'json'
    output_directory = sys.argv[3] if len(sys.argv) > 3 else '/files/crawl-output'
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Configure and run the crawler
    settings = get_project_settings()
    settings.update(SCRAPY_SETTINGS)
    
    process = CrawlerProcess(settings)
    process.crawl(SEOCrawlSpider, domain=domain, output_format=output_format, output_dir=output_directory)
    process.start()