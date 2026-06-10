import requests
from bs4 import BeautifulSoup
from app.extensions import db
from app.models import Scholarship

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# 1. OPPORTUNITY DESK
def scrape_opportunity_desk():
    # switched to Scholarship Positions — high-volume listings
    url = "https://scholarship-positions.com/category/scholarships/"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        posts = soup.find_all("article")

        added = 0

        for post in posts:
            title_tag = post.find("h2")
            link_tag = post.find("a")

            if not title_tag or not link_tag:
                continue

            title = title_tag.text.strip()
            link = link_tag["href"]

            exists = Scholarship.query.filter_by(application_link=link).first()
            if exists:
                continue

            db.session.add(Scholarship(
                title=title,
                provider="Scholarship Positions",
                application_link=link,
                description=title
            ))

            added += 1

        db.session.commit()
        return added

    except:
        return 0



# 2. SCHOLARSHIPS.COM
# (light scrape - limited HTML access)
def scrape_scholarships_com():
    # switched to Scholars4Dev — many international scholarship posts
    url = "https://www.scholars4dev.com/category/scholarships/"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a")

        added = 0

        for link in links[:20]:
            title = link.text.strip()
            href = link.get("href")

            if not title or not href:
                continue

            full_link = href if href.startswith("http") else "https://www.scholars4dev.com" + href

            exists = Scholarship.query.filter_by(application_link=full_link).first()
            if exists:
                continue

            db.session.add(Scholarship(
                title=title,
                provider="Scholars4Dev",
                application_link=full_link,
                description=title
            ))

            added += 1

        db.session.commit()
        return added

    except:
        return 0


# 3. SCHOLARSHIP PORTAL (basic)
def scrape_scholarship_portal():
    # switched to InternationalStudent scholarships listing
    url = "https://www.internationalstudent.com/scholarships/"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        cards = soup.find_all("a")

        added = 0

        for card in cards[:20]:
            title = card.text.strip()
            link = card.get("href")

            if not title or not link:
                continue

            full_link = link if link.startswith("http") else "https://www.internationalstudent.com" + link

            exists = Scholarship.query.filter_by(application_link=full_link).first()
            if exists:
                continue

            db.session.add(Scholarship(
                title=title,
                provider="International Student",
                application_link=full_link,
                description=title
            ))

            added += 1

        db.session.commit()
        return added

    except:
        return 0


# MASTER RUNNER

def run_all_scrapers():

    total = 0

    total += scrape_opportunity_desk()
    total += scrape_scholarships_com()
    total += scrape_scholarship_portal()

    return {
        "message": "Scraping completed",
        "total_added": total
    }