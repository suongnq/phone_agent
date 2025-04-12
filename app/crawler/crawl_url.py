import json
from datetime import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


class UrlCrawler:
    def __init__(self):
        pass

    def series_url(self, links, url):
        data = []
        for link in links:
            # Get links
            href = link.get_attribute("href")
            if not href.startswith("http") and not href.startswith("/"):
                href = url + "/" + href
            else:
                href = url + href

            img = link.query_selector("img")
            text = img.get_attribute("alt") if img else link.text_content()
            if not text:
                img = link.query_selector("img")
                if img:
                    text = img.get_attribute("alt") or link.get_attribute("title")
                else:
                    text = None
            # Data
            data.append(
                {
                    "web_url": url,
                    "phone_series_type": text,
                    "phone_series_url": href,
                    "time": datetime.today(),
                }
            )
        return data

    def items_url(self, links, url):
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        data = []
        for link in links:
            href = link.get_attribute("href")
            if not href.startswith("http") and not href.startswith("/"):
                href = domain + "/" + href
            else:
                href = domain + href

            data.append(
                {"phone_series_url": url, "item_url": href, "time": datetime.today()}
            )
        return data

    def crawling(self, url, crawl_type, selectors_info):
        # Crawling:
        data = []
        error = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                # Open browser
                page.goto(url, timeout=80000)
                print(f"------ {crawl_type } :{url}")

                # Get selector
                if crawl_type == "phone_series_url":
                    more_button = selectors_info["more_series_button"]
                    selector = selectors_info["url_series_selector"]
                else:
                    more_button = selectors_info["more_item_button"]
                    selector = selectors_info["url_items_selector"]
                # Open more
                try:
                    click_count = 0
                    max_clicks = 10
                    while click_count < max_clicks:
                        page.wait_for_timeout(5000)
                        page.click(more_button)
                        click_count += 1
                        page.wait_for_timeout(8000)
                except Exception as e:
                    try:
                        page.locator(more_button).nth(1).click()
                        page.wait_for_timeout(5000)
                    except Exception as e2:
                        pass

                # Access elements
                links = page.query_selector_all(selector)
                if crawl_type == "phone_series_url":
                    data = self.series_url(links, url)
                else:
                    data = self.items_url(links, url)

        except Exception as e:
            error.append({"url": url, "time": datetime.today()})

        print("------ Finish crawl")
        # Close browser
        try:
            browser.close()
        except Exception as e2:
            pass

        return data, error
