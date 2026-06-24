import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import xml.etree.ElementTree as ET
from app.extensions import db
from app.models import Scholarship

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

REQUEST_TIMEOUT = 20
DETAIL_TIMEOUT = 12

JUNK_KEYWORDS = [
    "clock", "alarm", "menu", "navigation", "login", "register",
    "home", "list item", "sidebar", "footer", "widget", "search",
    "category", "tag", "pagination", "sort", "filter", "advertisement",
    "skip to content", "loading", "cookie", "share on"
]

SKIP_URL_PATTERNS = [
    "/login", "/signin", "/register", "/signup",
    "/tag/", "/search", "/page/",
    "/search-results", "?", "#"
]


class ScraperStats:
    def __init__(self, provider):
        self.provider = provider
        self.cards_found = 0
        self.valid_items = 0
        self.added = 0
        self.duplicates = 0
        self.invalid = 0
        self.errors = 0

    def log_skipped(self, title, link, reason):
        print(f"\n  Source: {self.provider}")
        print(f"  Title: {title}")
        print(f"  Link: {link}")
        print(f"  Reason: {reason}")

    def log_added(self, title, link):
        print(f"  Status: ADDED")
        print(f"  Title: {title}")
        print(f"  Link: {link}")

    def print_summary(self):
        print(f"\n  =================================================")
        print(f"  SOURCE: {self.provider}")
        print(f"  =================================================")
        print(f"  Cards Found: {self.cards_found}")
        print(f"  Valid Items: {self.valid_items}")
        print(f"  Added: {self.added}")
        print(f"  Duplicates: {self.duplicates}")
        print(f"  Invalid: {self.invalid}")
        print(f"  Errors: {self.errors}")


def is_valid_title(title):
    if not title or len(title.strip()) < 10:
        return False, "Title too short"
    title_lower = title.lower()
    for keyword in JUNK_KEYWORDS:
        if keyword in title_lower:
            return False, f"Contains junk keyword: {keyword}"
    return True, "Valid"


def is_valid_url(url, base_url):
    if not url:
        return False, "Empty URL"
    full_url = urljoin(base_url, url)
    if full_url.startswith("javascript:") or full_url.startswith("#"):
        return False, "Invalid protocol"
    url_lower = full_url.lower()
    for pattern in SKIP_URL_PATTERNS:
        if pattern in url_lower:
            return False, f"Matches skip pattern: {pattern}"
    parsed = urlparse(full_url)
    if not parsed.path or parsed.path in ["", "/"]:
        return False, "Homepage URL"
    return True, full_url


URL_RE = re.compile(r'^https?://', re.IGNORECASE)


def extract_description(element, title):
    meta = element.find("meta", {"name": "description"})
    if meta and meta.get("content"):
        desc = meta.get("content").strip()
        if desc and len(desc) > 5 and not URL_RE.match(desc):
            return desc
    p_tags = element.find_all("p")
    for p in p_tags:
        text = p.text.strip()
        hrefs = p.find_all("a")
        nav_hrefs = [a for a in hrefs if a.get("href") and "/category/" in a.get("href").lower()]
        if nav_hrefs:
            continue
        if text and len(text) > 20 and len(text) < 500 and not URL_RE.match(text):
            return text[:500]
    return title


def check_duplicate(link, title):
    exists_by_link = Scholarship.query.filter_by(application_link=link).first()
    if exists_by_link:
        return True, "Duplicate link"
    normalized_title = " ".join(title.split()).lower()
    exists_by_title = Scholarship.query.filter(
        db.func.lower(db.func.replace(Scholarship.title, " ", "")) ==
        db.func.lower(db.func.replace(normalized_title, " ", ""))
    ).first()
    if exists_by_title:
        return True, "Duplicate title"
    return False, "New"


def is_url_like(text):
    return bool(URL_RE.match(text.strip()))


PILL_PATTERNS = re.compile(
    r'(Master|PhD|Doctoral|Bachelor|Undergraduate|Graduate|Postdoc|'
    r'Postdoctoral|Fellowship|Masters|Bachelors|M\.Sc|M\.A\.|Ph\.D)',
    re.IGNORECASE
)


def parse_deadline(text):
    if not text:
        return None
    text = text.strip()
    patterns = [
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            for fmt in ['%d %B %Y', '%d %b %Y', '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
    return None


def extract_detail_fields(detail_soup, base_url):
    result = {
        'deadline': None,
        'degree_level': None,
        'eligibility': None,
        'application_link': base_url,
        'description': None
    }

    full_text = detail_soup.get_text(" ", strip=True)
    result['deadline'] = parse_deadline(full_text)

    degree_match = re.search(
        r'(degree level|level of study|study level)[:\s]+([A-Za-z\s/]+?)(?:\.|$|\n)',
        full_text, re.IGNORECASE
    )
    if degree_match:
        result['degree_level'] = degree_match.group(2).strip()[:200]

    eligibility_match = re.search(
        r'(eligibility|who can apply|requirements)[:\s]+([A-Za-z\s,;.\-()]+?)(?:\.(?:\s|$)|$)',
        full_text, re.IGNORECASE
    )
    if eligibility_match:
        result['eligibility'] = eligibility_match.group(2).strip()[:300]

    meta_desc = detail_soup.find("meta", {"name": "description"})
    if meta_desc and meta_desc.get("content"):
        result['description'] = meta_desc.get("content").strip()[:500]

    for sel in [
        'a[href*="apply"]', 'a[href*="application"]', 'a[href*="register"]',
        '.apply-btn a', '.btn-apply a', 'a.apply-link'
    ]:
        try:
            link = detail_soup.select_one(sel)
            if link and link.get('href'):
                result['application_link'] = urljoin(base_url, link['href'])
                break
        except Exception:
            continue

    return result


def create_scholarship(title, provider, link, description, country="Global", deadline=None, degree_level=None, eligibility=None, application_link=None):
    if is_url_like(description):
        description = title
    s = Scholarship(
        title=title, provider=provider, country=country,
        application_link=application_link or link,
        description=description, deadline=deadline,
        degree_level=degree_level, eligibility=eligibility
    )
    db.session.add(s)


def parse_rss_feed(feed_url, provider):
    """Generic RSS feed parser for WordPress-based scholarship sites."""
    stats = ScraperStats(provider)
    added = 0
    try:
        res = requests.get(feed_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        res.raise_for_status()
        root = ET.fromstring(res.content)
        ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}

        channel = root.find('channel')
        items = channel.findall('item') if channel is not None else root.findall('.//item')

        stats.cards_found = len(items)

        for item in items:
            title_el = item.find('title')
            link_el = item.find('link')
            if title_el is None or link_el is None:
                stats.invalid += 1
                continue

            title = title_el.text.strip() if title_el.text else ''
            href = link_el.text.strip() if link_el.text else ''

            valid_title, reason = is_valid_title(title)
            if not valid_title:
                stats.invalid += 1
                stats.log_skipped(title, href, reason)
                continue

            valid_url, resolved = is_valid_url(href, href)
            if not valid_url:
                stats.invalid += 1
                stats.log_skipped(title, href, resolved)
                continue

            is_dup, dup_reason = check_duplicate(resolved, title)
            if is_dup:
                stats.duplicates += 1
                stats.log_skipped(title, resolved, dup_reason)
                continue

            description = ''
            desc_el = item.find('description')
            if desc_el is not None and desc_el.text:
                desc_soup = BeautifulSoup(desc_el.text, 'html.parser')
                description = desc_soup.get_text(' ', strip=True)[:500]

            content_el = item.find('content:encoded', ns)
            full_text = ''
            if content_el is not None and content_el.text:
                content_soup = BeautifulSoup(content_el.text, 'html.parser')
                full_text = content_soup.get_text(' ', strip=True)
            elif description:
                full_text = description

            deadline = parse_deadline(full_text) if full_text else None
            country = 'Global'
            categories = item.findall('category')
            if categories:
                cat_texts = [c.text for c in categories if c.text]
                for c in cat_texts:
                    if c.lower() in ['germany', 'usa', 'uk', 'canada', 'australia', 'japan', 'china', 'france', 'sweden', 'netherlands', 'switzerland', 'south korea']:
                        country = c.title()
                        break

            degree_level = None
            degree_match = PILL_PATTERNS.search(title + ' ' + full_text)
            if degree_match:
                degree_level = degree_match.group(1)

            create_scholarship(title, provider, resolved, description, country, deadline, degree_level)
            added += 1
            stats.added += 1
            stats.log_added(title, resolved)

        db.session.commit()
        stats.print_summary()
        return added
    except requests.RequestException as e:
        stats.errors += 1
        print(f"[ERROR] RSS feed {provider}: {e}")
        stats.print_summary()
        return 0
    except ET.ParseError as e:
        stats.errors += 1
        print(f"[ERROR] XML parse for {provider}: {e}")
        stats.print_summary()
        return 0
    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {e}")
        db.session.rollback()
        stats.print_summary()
        return 0


# --- SCRAPERS ---

def scrape_opportunity_desk():
    provider = "Scholarship Positions"
    url = "https://scholarship-positions.com/category/scholarships/"
    stats = ScraperStats(provider)
    added = 0

    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")

        entries = (
            soup.find_all("article")
            or soup.find_all("div", class_=lambda c: c and ("post" in c.lower() or "entry" in c.lower()))
            or soup.find_all("li", class_=lambda c: c and "post" in c.lower())
        )

        for post in entries:
            stats.cards_found += 1
            title_tag = post.find("h2") or post.find("h3") or post.find("a", class_=lambda c: c and "title" in c.lower())
            if not title_tag:
                stats.invalid += 1
                continue

            title = title_tag.get_text(strip=True)
            valid_title, reason = is_valid_title(title)
            if not valid_title:
                stats.invalid += 1
                continue

            link_tag = post.find("a") if title_tag.name != 'a' else title_tag
            if not link_tag:
                stats.invalid += 1
                continue
            href = link_tag.get("href")
            valid_url, resolved = is_valid_url(href, url)
            if not valid_url:
                stats.invalid += 1
                continue

            is_dup, reason = check_duplicate(resolved, title)
            if is_dup:
                stats.duplicates += 1
                continue

            description = extract_description(post, title)
            create_scholarship(title, provider, resolved, description)
            added += 1
            stats.added += 1
            stats.log_added(title, resolved)

        db.session.commit()
        stats.print_summary()
        return added
    except requests.RequestException as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {e}")
        stats.print_summary()
        return 0
    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {e}")
        db.session.rollback()
        stats.print_summary()
        return 0


def scrape_scholars4dev():
    return parse_rss_feed("https://www.scholars4dev.com/feed/", "Scholars4Dev")


def scrape_international_student():
    provider = "International Student"
    url = "https://www.internationalstudent.com/scholarships/"
    base_url = "https://www.internationalstudent.com"
    stats = ScraperStats(provider)
    added = 0

    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")

        main = soup.find("main") or soup.find("div", class_="content") or soup.find("div", id="content")
        if not main:
            stats.print_summary()
            return 0

        entries = (
            main.find_all("article")
            or main.find_all("div", class_=lambda c: c and ("result" in c.lower() or "listing" in c.lower() or "item" in c.lower()))
            or main.find_all("tr")
        )

        for entry in entries:
            link_tag = entry.find("a")
            if not link_tag:
                continue
            title = link_tag.get_text(strip=True)
            href = link_tag.get("href", "")
            if not title or not href:
                continue

            valid_title, reason = is_valid_title(title)
            if not valid_title:
                stats.invalid += 1
                continue
            valid_url, resolved = is_valid_url(href, base_url)
            if not valid_url:
                stats.invalid += 1
                stats.log_skipped(title, href, resolved)
                continue
            is_dup, reason = check_duplicate(resolved, title)
            if is_dup:
                stats.duplicates += 1
                continue

            description = extract_description(entry, title)
            create_scholarship(title, provider, resolved, description)
            added += 1
            stats.added += 1
            stats.log_added(title, resolved)

        db.session.commit()
        stats.print_summary()
        return added
    except requests.RequestException as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {e}")
        stats.print_summary()
        return 0
    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {e}")
        db.session.rollback()
        stats.print_summary()
        return 0


def scrape_opportunitydesk():
    return parse_rss_feed("https://opportunitydesk.org/feed/", "Opportunity Desk")


def run_all_scrapers():
    from app.scraping.seed_data import seed_scholarships

    print("\n" + "="*60)
    print("SCHOLARSHIP SCRAPER - Starting run")
    print("="*60)

    total = 0
    total += scrape_opportunity_desk()
    total += scrape_scholars4dev()
    total += scrape_international_student()
    total += scrape_opportunitydesk()

    seeded = seed_scholarships()
    total += seeded

    print("\n" + "="*60)
    print(f"SCRAPING COMPLETED - Total scholarships added: {total}")
    print("="*60 + "\n")

    return {"message": "Scraping completed", "total_added": total}
