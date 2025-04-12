import json
from datetime import datetime
from playwright.sync_api import sync_playwright


class ItemDetailCrawler:
    def __init__(self):
        pass

    def get_cats_path(self, selector, page):
        try:
            cats = page.query_selector_all(selector["cats_path_selector"])
            cats_values = [cate.inner_text() for cate in cats]
            cats_path = "|".join(cats_values)
        except Exception as e1:
            cats_path = None

        return cats_path

    def get_item_name(self, selector, page):
        # Get item name
        try:
            item_name_node = page.query_selector(selector["item_name_selector"])
            item_name = item_name_node.inner_text()
        except Exception as e2:
            item_name = None
        return item_name

    def get_storage_capacity(self, selector, page):
        # Get storage capacity
        try:
            storage_capacity_node = page.query_selector(
                selector["storage_capacity_selector"]
            ).query_selector("strong")
            storage_capacity = storage_capacity_node.inner_text()
        except:
            try:
                storage_capacity_node = page.query_selector_all(
                    selector["storage_capacity_selector"]
                )
                if len(storage_capacity_node) >= 2:
                    storage_capacity = storage_capacity_node[0].inner_text()
                else:
                    storage_capacity = None
            except:
                storage_capacity = None

        return storage_capacity

    def get_color(self, selector, page):
        # Get color
        try:
            color_nodes = page.query_selector_all(selector["color_selector"])
            color = color_nodes[0].inner_text()
            if selector["color_selector"] == selector["storage_capacity_selector"]:
                color = color_nodes[-1].inner_text()
        except:
            color = None
        return color

    def get_price(self, selector, page):
        # Get price
        try:
            price_node = page.query_selector(selector["price_selector"])
            price = price_node.inner_text()
        except Exception as e5:
            price = None
        return price

    def get_rating(self, selector, page):
        # Get rating
        try:
            rating_node = page.query_selector(selector["rating_selector"])
            rating = rating_node.inner_text()
        except:
            try:
                rating_node = page.query_selector_all(selector["rating_selector"])[-1]
                rating = rating_node.inner_text()
            except:
                rating = None
        return rating

    def get_num_review(self, selector, page):
        # Get num reviews
        try:
            num_reviews_node = page.query_selector(selector["num_reviews_selector"])
            num_reviews = num_reviews_node.inner_text()
        except:
            try:
                num_reviews_node = page.query_selector_all(
                    selector["num_reviews_selector"]
                )[-1]
                num_reviews = num_reviews_node.inner_text()
            except:
                num_reviews = None
        return num_reviews

    def crawling(self, url, selector):
        error = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                # Open browser
                page.goto(url, timeout=100000)
                # Get information:
                cats_path = self.get_cats_path(selector, page)
                item_name = self.get_item_name(selector, page)
                storage_capacity = self.get_storage_capacity(selector, page)
                color = self.get_color(selector, page)
                price = self.get_price(selector, page)
                rating = self.get_rating(selector, page)
                num_review = self.get_num_review(selector, page)
                if item_name is None and price is None and color is None:
                    pass
                else:
                    data = []
                    # Build data
                    data.append(
                        {
                            "item_url": url,
                            "cats_path": cats_path,
                            "item_name": item_name,
                            "storage_capacity": storage_capacity,
                            "color": color,
                            "price": price,
                            "rating": rating,
                            "num_review": num_review,
                            "time": datetime.today(),
                        }
                    )
                    print(data)

                try:
                    browser.close()
                except Exception as e2:
                    pass
        except Exception as e:
            error.append({"url": url, "time": datetime.today()})

        return data, error
