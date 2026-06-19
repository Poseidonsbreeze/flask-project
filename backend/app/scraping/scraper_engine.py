import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.extensions import db
from app.models import Scholarship

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

REQUEST_TIMEOUT = 15

JUNK_KEYWORDS = [
    "clock", "alarm", "menu", "navigation", "login", "register",
    "home", "list item", "sidebar", "footer", "widget", "search",
    "category", "tag", "pagination", "sort", "filter", "advertisement"
]

SKIP_URL_PATTERNS = [
    "/login", "/signin", "/register", "/signup",
    "/category/", "/tag/", "/search", "/page/",
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


def create_scholarship(title, provider, link, description, country="Global"):
    if is_url_like(description):
        description = title
    scholarship = Scholarship(
        title=title,
        provider=provider,
        country=country,
        application_link=link,
        description=description,
        deadline=None
    )
    db.session.add(scholarship)


# 1. OPPORTUNITY DESK
def scrape_opportunity_desk():
    provider = "Scholarship Positions"
    url = "https://scholarship-positions.com/category/scholarships/"
    stats = ScraperStats(provider)
    added = 0

    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")
        posts = soup.find_all("article")

        for post in posts:
            stats.cards_found += 1
            title_tag = post.find("h2")
            if not title_tag:
                stats.invalid += 1
                continue
            title = title_tag.text.strip()

            is_valid, reason = is_valid_title(title)
            if not is_valid:
                stats.invalid += 1
                stats.log_skipped(title, "N/A", reason)
                continue

            link_tag = post.find("a")
            if not link_tag:
                stats.invalid += 1
                stats.log_skipped(title, "N/A", "No link found")
                continue

            href = link_tag.get("href")
            is_valid_url_result, resolved_link = is_valid_url(href, url)
            if not is_valid_url_result:
                stats.invalid += 1
                stats.log_skipped(title, href or "N/A", resolved_link)
                continue

            is_duplicate, dup_reason = check_duplicate(resolved_link, title)
            if is_duplicate:
                stats.duplicates += 1
                stats.log_skipped(title, resolved_link, dup_reason)
                continue

            stats.valid_items += 1
            description = extract_description(post, title)
            create_scholarship(title, provider, resolved_link, description)
            added += 1
            stats.added += 1
            stats.log_added(title, resolved_link)

        db.session.commit()
        stats.print_summary()
        return added

    except requests.RequestException as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: Network error - {str(e)}")
        stats.print_summary()
        return 0
    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {str(e)}")
        db.session.rollback()
        stats.print_summary()
        return 0


# 2. SCHOLARS4DEV
def scrape_scholars4dev():
    url = "https://www.scholars4dev.com/category/scholarships/"
    provider = "Scholars4Dev"
    base_url = "https://www.scholars4dev.com"
    stats = ScraperStats(provider)
    added = 0

    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.find_all("article") or soup.find_all("div", class_="post")

        for article in articles:
            stats.cards_found += 1
            link_tag = article.find("a")
            if not link_tag:
                stats.invalid += 1
                continue

            title = link_tag.text.strip()
            href = link_tag.get("href")

            is_valid, reason = is_valid_title(title)
            if not is_valid:
                stats.invalid += 1
                stats.log_skipped(title, href or "N/A", reason)
                continue

            is_valid_url_result, resolved_link = is_valid_url(href, base_url)
            if not is_valid_url_result:
                stats.invalid += 1
                stats.log_skipped(title, href or "N/A", resolved_link)
                continue

            is_duplicate, dup_reason = check_duplicate(resolved_link, title)
            if is_duplicate:
                stats.duplicates += 1
                stats.log_skipped(title, resolved_link, dup_reason)
                continue

            stats.valid_items += 1
            description = extract_description(article, title)
            create_scholarship(title, provider, resolved_link, description)
            added += 1
            stats.added += 1
            stats.log_added(title, resolved_link)

        db.session.commit()
        stats.print_summary()
        return added

    except requests.RequestException as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: Network error - {str(e)}")
        stats.print_summary()
        return 0
    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {str(e)}")
        db.session.rollback()
        stats.print_summary()
        return 0


# 3. DAAD
def scrape_daad():
    provider = "DAAD"
    url = "https://www.daad.de/en/study-and-research-in-germany/scholarships/"
    base_url = "https://www.daad.de"
    stats = ScraperStats(provider)
    added = 0
    valid_extracted = 0
    skipped = 0
    total_cards_found = 0

    def is_valid_daad_title(t):
        t_norm = (t or "").strip()
        if not t_norm:
            return False
        t_lower = t_norm.lower()
        if t_lower in {"home", "daad"}:
            return False
        return True

    def extract_country_from_text(text):
        if not text:
            return None
        lowered = text.lower()
        for marker in ["germany", "deutschland", "usa", "canada", "uk", "united kingdom", "australia"]:
            if marker in lowered:
                return "Germany" if "germany" in marker or "deutschland" in marker else marker.title()
        return None

    def parse_listing_page(soup):
        nonlocal total_cards_found, valid_extracted, skipped, added

        containers = (
            soup.find_all("article")
            or soup.find_all("div", class_=lambda c: c and ("card" in c or "teaser" in c or "listing" in c or "result" in c))
            or soup.find_all("section")
        )
        if not containers:
            containers = [soup]

        seen_titles_links = set()

        for container in containers:
            for a in container.find_all("a"):
                title = a.get_text(strip=True)
                href = a.get("href") or ""
                if not title or len(title) < 2:
                    continue

                if not is_valid_daad_title(title):
                    skipped += 1
                    continue

                resolved_try = urljoin(base_url, href) if href else ""
                key = (" ".join(title.split()).lower(), resolved_try)
                if key in seen_titles_links:
                    continue
                seen_titles_links.add(key)
                total_cards_found += 1
                stats.cards_found += 1

                is_valid, reason = is_valid_title(title)
                if not is_valid:
                    skipped += 1
                    stats.invalid += 1
                    stats.log_skipped(title, href, reason)
                    continue

                href_norm = (href or "").strip()
                if href_norm in {"/", "#"} or href_norm.startswith("#"):
                    skipped += 1
                    stats.invalid += 1
                    stats.log_skipped(title, href, "Invalid URL pattern")
                    continue

                is_valid_url_result, resolved_link = is_valid_url(href, base_url)
                if not is_valid_url_result:
                    skipped += 1
                    stats.invalid += 1
                    stats.log_skipped(title, href, resolved_link)
                    continue

                is_duplicate, dup_reason = check_duplicate(resolved_link, title)
                if is_duplicate:
                    skipped += 1
                    stats.duplicates += 1
                    stats.log_skipped(title, resolved_link, dup_reason)
                    continue

                container_text = container.get_text(" ", strip=True)
                country = extract_country_from_text(container_text) or "International"

                description = ""
                meta = container.find("meta", {"name": "description"})
                if meta and meta.get("content"):
                    description = meta.get("content").strip()
                if not description:
                    for p in container.find_all("p"):
                        text = p.get_text(" ", strip=True)
                        if text and 20 < len(text) < 600:
                            description = text[:500]
                            break
                if not description:
                    candidate_desc = extract_description(container, title)
                    description = candidate_desc if candidate_desc and candidate_desc != title else ""

                valid_extracted += 1
                stats.valid_items += 1
                create_scholarship(title, provider, resolved_link, description, country)
                added += 1
                stats.added += 1
                stats.log_added(title, resolved_link)

    try:
        session = requests.Session()
        next_url = url
        seen_pages = set()

        while next_url and next_url not in seen_pages:
            seen_pages.add(next_url)
            res = session.get(next_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            parse_listing_page(soup)

            next_link = None
            for a in soup.find_all("a"):
                text = (a.get_text(strip=True) or "").lower()
                rel = (a.get("rel") or "").lower()
                aria = (a.get("aria-label") or "").lower()
                if "next" in text or rel == "next" or "next" in aria:
                    href = a.get("href")
                    if href:
                        candidate = urljoin(base_url, href)
                        if candidate and candidate != next_url:
                            next_link = candidate
                            break

            if not next_link:
                for a in soup.find_all("a"):
                    href = a.get("href") or ""
                    href_lower = href.lower()
                    if any(pat in href_lower for pat in ["page=", "?page=", "/page/", "offset=", "start="]):
                        candidate = urljoin(base_url, href)
                        if candidate and candidate != next_url:
                            next_link = candidate
                            break

            next_url = next_link

        db.session.commit()
        stats.print_summary()
        return added

    except requests.RequestException as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: Network error - {str(e)}")
        stats.print_summary()
        return 0
    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {str(e)}")
        db.session.rollback()
        stats.print_summary()
        return 0


# 4. INTERNATIONAL STUDENT
def scrape_international_student():
    url = "https://www.internationalstudent.com/scholarships/"
    provider = "International Student"
    base_url = "https://www.internationalstudent.com"
    stats = ScraperStats(provider)
    added = 0

    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, "html.parser")

        main_content = soup.find("article") or soup.find("main") or soup.find("div", class_="container")
        if not main_content:
            print(f"[WARNING] {provider}: Could not find main content area")
            stats.print_summary()
            return 0

        for breadcrumb in main_content.find_all("ul", class_="breadcrumb"):
            breadcrumb.decompose()
        for nav in main_content.find_all("nav"):
            nav.decompose()

        articles = main_content.find_all("article")
        if not articles:
            articles = main_content.find_all("div", class_=lambda c: c and ("post" in c.lower() or "entry" in c.lower() or "item" in c.lower()))
        if not articles:
            articles = [main_content]

        for article in articles:
            link_tag = article.find("a")
            if not link_tag:
                continue

            title = link_tag.text.strip()
            href = link_tag.get("href", "")

            if not title or len(title.strip()) < 5:
                stats.invalid += 1
                continue

            is_valid, reason = is_valid_title(title)
            if not is_valid:
                stats.invalid += 1
                stats.log_skipped(title, href or "N/A", reason)
                continue

            is_valid_url_result, resolved_link = is_valid_url(href, base_url)
            if not is_valid_url_result:
                stats.invalid += 1
                stats.log_skipped(title, href or "N/A", resolved_link)
                continue

            is_duplicate, dup_reason = check_duplicate(resolved_link, title)
            if is_duplicate:
                stats.duplicates += 1
                stats.log_skipped(title, resolved_link, dup_reason)
                continue

            description = extract_description(article, title)
            create_scholarship(title, provider, resolved_link, description)
            added += 1
            stats.added += 1
            stats.log_added(title, resolved_link)

        db.session.commit()
        stats.print_summary()
        return added

    except requests.RequestException as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: Network error - {str(e)}")
        stats.print_summary()
        return 0
    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {str(e)}")
        db.session.rollback()
        stats.print_summary()
        return 0


# 5. OPPORTUNITYDESK (new scraper)
def scrape_opportunitydesk():
    provider = "Opportunity Desk"
    base_url = "https://opportunitydesk.org"
    stats = ScraperStats(provider)
    added = 0

    scholarship_categories = [
        "/category/scholarships/undergraduate/",
        "/category/scholarships/short-courses/",
        "/category/scholarships/online-courses/",
        "/category/scholarships/masters-postgraduate/",
        "/category/scholarships/phd/",
        "/category/scholarships/postdoctoral/",
        "/category/scholarships/study-abroad/",
    ]

    generic_titles = ["opportunity desk"]

    def is_not_generic(title):
        t = title.strip().lower()
        return t not in generic_titles and "opportunity desk" not in t

    try:
        session = requests.Session()

        for category_path in scholarship_categories:
            page_url = urljoin(base_url, category_path)
            try:
                res = session.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                res.raise_for_status()
            except requests.RequestException as e:
                stats.errors += 1
                print(f"[WARNING] {provider}: Skipping {category_path} - {str(e)}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            articles = soup.find_all("article")
            if not articles:
                articles = soup.find_all("div", class_=lambda c: c and "post" in c.lower()) or []
            if not articles:
                articles = soup.find_all("div", class_=lambda c: c and "listing" in c.lower()) or []

            for article in articles:
                stats.cards_found += 1

                title_tag = article.find("h2") or article.find("h3") or article.find("h4")
                if not title_tag:
                    title_tag = article.find("a")
                if not title_tag:
                    stats.invalid += 1
                    continue

                title = title_tag.get_text(strip=True)
                if not title:
                    stats.invalid += 1
                    continue

                if not is_not_generic(title):
                    stats.invalid += 1
                    stats.log_skipped(title, "N/A", "Generic title")
                    continue

                is_valid, reason = is_valid_title(title)
                if not is_valid:
                    stats.invalid += 1
                    stats.log_skipped(title, "N/A", reason)
                    continue

                link_tag = article.find("a")
                if not link_tag:
                    stats.invalid += 1
                    stats.log_skipped(title, "N/A", "No link found")
                    continue

                href = link_tag.get("href")
                if not href or href in ["/", "#"] or href.startswith("javascript:"):
                    stats.invalid += 1
                    stats.log_skipped(title, href or "N/A", "Invalid link")
                    continue

                is_valid_url_result, resolved_link = is_valid_url(href, base_url)
                if not is_valid_url_result:
                    stats.invalid += 1
                    stats.log_skipped(title, href or "N/A", resolved_link)
                    continue

                is_duplicate, dup_reason = check_duplicate(resolved_link, title)
                if is_duplicate:
                    stats.duplicates += 1
                    stats.log_skipped(title, resolved_link, dup_reason)
                    continue

                stats.valid_items += 1
                description = extract_description(article, title)
                country = "Global"

                cat_tag = article.find(class_=lambda c: c and ("cat" in c.lower() or "term" in c.lower() or "tag" in c.lower()))
                if cat_tag:
                    country = cat_tag.get_text(strip=True) or "Global"

                create_scholarship(title, provider, resolved_link, description, country)
                added += 1
                stats.added += 1
                stats.log_added(title, resolved_link)

            pagination = soup.find("a", class_="next") or soup.find("a", string="Next") or soup.find("a", string=lambda s: s and "next" in s.lower())
            page_num = 2
            while pagination:
                try:
                    next_url = pagination.get("href") or f"{category_path}page/{page_num}/"
                    next_url = urljoin(base_url, next_url)
                    page_res = session.get(next_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                    page_res.raise_for_status()
                except requests.RequestException as e:
                    break

                page_soup = BeautifulSoup(page_res.text, "html.parser")
                page_articles = page_soup.find_all("article") or page_soup.find_all("div", class_=lambda c: c and ("post" in c.lower() or "listing" in c.lower())) or []

                if not page_articles:
                    break

                for article in page_articles:
                    stats.cards_found += 1

                    title_tag = article.find("h2") or article.find("h3") or article.find("h4")
                    if not title_tag:
                        title_tag = article.find("a")
                    if not title_tag:
                        stats.invalid += 1
                        continue

                    title = title_tag.get_text(strip=True)
                    if not title:
                        stats.invalid += 1
                        continue

                    if not is_not_generic(title):
                        stats.invalid += 1
                        stats.log_skipped(title, "N/A", "Generic title")
                        continue

                    is_valid, reason = is_valid_title(title)
                    if not is_valid:
                        stats.invalid += 1
                        stats.log_skipped(title, "N/A", reason)
                        continue

                    link_tag = article.find("a")
                    if not link_tag:
                        stats.invalid += 1
                        stats.log_skipped(title, "N/A", "No link found")
                        continue

                    href = link_tag.get("href")
                    if not href or href in ["/", "#"] or href.startswith("javascript:"):
                        stats.invalid += 1
                        stats.log_skipped(title, href or "N/A", "Invalid link")
                        continue

                    is_valid_url_result, resolved_link = is_valid_url(href, base_url)
                    if not is_valid_url_result:
                        stats.invalid += 1
                        stats.log_skipped(title, href or "N/A", resolved_link)
                        continue

                    is_duplicate, dup_reason = check_duplicate(resolved_link, title)
                    if is_duplicate:
                        stats.duplicates += 1
                        stats.log_skipped(title, resolved_link, dup_reason)
                        continue

                    stats.valid_items += 1
                    description = extract_description(article, title)
                    country = "Global"
                    cat_tag = article.find(class_=lambda c: c and ("cat" in c.lower() or "term" in c.lower() or "tag" in c.lower()))
                    if cat_tag:
                        country = cat_tag.get_text(strip=True) or "Global"

                    create_scholarship(title, provider, resolved_link, description, country)
                    added += 1
                    stats.added += 1
                    stats.log_added(title, resolved_link)

                page_num += 1
                pagination = page_soup.find("a", class_="next") or page_soup.find("a", string="Next") or page_soup.find("a", string=lambda s: s and "next" in s.lower())
                if not pagination:
                    break

        db.session.commit()
        stats.print_summary()
        return added

    except Exception as e:
        stats.errors += 1
        print(f"[ERROR] {provider}: {str(e)}")
        db.session.rollback()
        stats.print_summary()
        return 0


# MASTER RUNNER
def run_all_scrapers():
    print("\n" + "="*60)
    print("SCHOLARSHIP SCRAPER - Starting run")
    print("="*60)

    total = 0
    total += scrape_opportunity_desk()
    total += scrape_scholars4dev()
    total += scrape_international_student()
    total += scrape_daad()
    total += scrape_opportunitydesk()

    print("\n" + "="*60)
    print(f"SCRAPING COMPLETED - Total scholarships added: {total}")
    print("="*60 + "\n")

    return {
        "message": "Scraping completed",
        "total_added": total
    }
