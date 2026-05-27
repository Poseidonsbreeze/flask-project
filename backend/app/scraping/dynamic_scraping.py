from playwright.sync_api import sync_playwright


def scrape_js_site(url):

    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        page.wait_for_timeout(5000)

        cards = page.query_selector_all("a")

        for card in cards[:20]:
            title = card.inner_text()
            link = card.get_attribute("href")

            if title:
                data.append({
                    "title": title,
                    "link": link
                })

        browser.close()

    return data