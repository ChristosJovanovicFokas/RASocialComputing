from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from collections import Counter
import re


class Parser:
    def __init__(self, html, logger=None):
        self.logger = logger
        self.html = html
        self.base_url = self.parse_base_url()
        self.soup = BeautifulSoup(html, "html.parser") if html else None

    def parse_css(self):
        return str(self.soup.find_all("style"))


    def parse_base_url(self):
        if not self.html:
            return None
        
        soup = BeautifulSoup(self.html, "html.parser")
        base_tag = soup.find("base", href=True)
        if base_tag:
            parsed = urlparse(base_tag["href"])
            return f"{parsed.scheme}://{parsed.netloc}"
        
        canonical = soup.find("link", rel="canonical", href=True)
        if canonical:
            parsed = urlparse(canonical["href"])
            return f"{parsed.scheme}://{parsed.netloc}"
        
        og_url = soup.find("meta", property="og:url", content=True)
        if og_url:
            parsed = urlparse(og_url["content"])
            return f"{parsed.scheme}://{parsed.netloc}"

        return None

    def parse_product_links(self):
        links = set()

        bad_ext = (
            ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
            ".pdf", ".zip", ".rar", ".gz",
            ".mp4", ".mp3", ".avi",
            ".css", ".js", ".json", ".xml"
        )

        #Keywords for parsing
        product_pattern = re.compile(
                r"/(product|products|shop|store|item|items|collections|"
                r"category|catalog|goods|detail|listing|p|pd|buy|sku)/"
            )

        for a in self.soup.find_all("a", href=True):
            
            href = a["href"].strip()

            if not href:
                continue

            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue

            if not href.startswith(("http://", "https://")):
                if self.base_url:
                    href = urljoin(str(self.base_url), href)
                else:
                    continue

            parsed = urlparse(href)
            path = parsed.path.lower()


            if any(path.endswith(ext) for ext in bad_ext):
                continue

            if not product_pattern.search(path):
                continue


            links.add(href)

        return list(links)

    def parse_about(self):
        MAIN_TAGS = ["main", "article", "section"]
        container = None
        for tag in MAIN_TAGS:
            container = self.soup.find(tag)
            if container:
                break
        
        #Fall back if there is no container
        if not container:
            container = self.soup.body

        if not container:
            return None
        
        filtered_tags = container.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"])
        html_snippet = "".join(str(tag) for tag in filtered_tags)

        return html_snippet if html_snippet else None
        

    #Parser for individual product listings
    def get_candidate_blocks(soup):
        return soup.find_all("div")
    

    def signature(self, tag):
        return (
            tag.name,
            " ".join(tag.get("class", [])),
            len(tag.find_all("img")),
            len(tag.find_all("a"))
        )
    

    def find_product_blocks(self):
        blocks = self.soup.find_all("div")

        groups = defaultdict(list)

        for b in blocks:
            sig = self.signature(b)
            groups[sig].append(b)

        # return largest repeated group (likely products)
        best_group = max(groups.values(), key=len)

        return best_group
    
    def parse_product(self):
        product_blocks = self.find_product_blocks()

        products = []

        for block in product_blocks:
            title = block.find("h1") or block.find("h2") or block.find("a")
            price = block.get_text(" ", strip=True)

            img = block.find("img")

            products.append({
                "title": title.get_text(strip=True) if title else None,
                "price": price,
                "image": img["src"] if img and img.get("src") else None,
                "raw": str(block)
            })

        return products



import os

if __name__ == "__main__":
    
    # Test 1 — real HTML file
    print("=== Test 1: Real HTML file ===")
    with open(r"data/html/products/0ecf5be392095a386441410ca235fd01/main.html", encoding="utf-8") as f:
        html = f.read()
    
    parser = Parser(html)
    print(f"Base URL detected: {parser.base_url}")
    links = parser.parse_product_links()
    print(f"Product links found: {len(links)}")
    for link in links[:5]:  # print first 5
        print(f"  {link}")

    # Test 2 — no HTML (edge case)
    print("\n=== Test 2: Empty HTML ===")
    parser_empty = Parser(None)
    print(f"Base URL: {parser_empty.base_url}")
    links_empty = parser_empty.parse_product_links() if parser_empty.soup else []
    print(f"Links found: {len(links_empty)}")

    # Test 3 — mock HTML with known product links
    print("\n=== Test 3: Mock HTML ===")
    mock_html = """
    <html>
    <head>
        <meta property="og:url" content="https://bestcologne.com/home"/>
    </head>
    <body>
        <a href="/products/cologne-a">Cologne A</a>
        <a href="/products/cologne-b">Cologne B</a>
        <a href="/about">About</a>
        <a href="/shop/item-123">Item 123</a>
        <a href="https://external.com/products/xyz">External</a>
        <a href="/images/banner.jpg">Image</a>
    </body>
    </html>
    """
    parser_mock = Parser(mock_html)
    print(f"Base URL detected: {parser_mock.base_url}")
    links_mock = parser_mock.parse_product_links()
    print(f"Product links found: {len(links_mock)}")
    for link in links_mock:
        print(f"  {link}")
    
    # Expected: cologne-a, cologne-b, item-123 found
    # Expected: about, banner.jpg, external.com NOT found
    assert len(links_mock) >= 3, "Should find at least 3 product links"
    assert not any("about" in l for l in links_mock), "Should not include about page"
    assert not any(".jpg" in l for l in links_mock), "Should not include images"
    print("All assertions passed")

    