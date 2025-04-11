import json
import re
from datetime import datetime

import fire
from playwright.sync_api import Playwright, TimeoutError, sync_playwright

input_date_format = "%b %d, %Y"
output_date_format = "%Y-%m-%d"


def get_ratings(playwright: Playwright, user_id: str) -> None:
    global captured_data
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    try:
        page.goto(f"https://www.imdb.com/user/{user_id}/ratings")
        page.wait_for_load_state("networkidle")

        films = page.locator("li.ipc-metadata-list-summary-item")
        for i in range(films.count()):
            item = films.nth(i)
            link = item.locator("a.ipc-title-link-wrapper").get_attribute("href")
            imdb_id = re.findall(r"tt\d+", link)[0]
            rating = (
                item.get_by_test_id("ratingGroup--other-user-rating")
                .locator("span.ipc-rating-star--rating")
                .inner_text()
            )
            if rating is None or rating == "":
                rating = "watched"
            date = item.locator("div.dli-user-list-item-date-added").inner_text()
            if date.startswith("Rated on"):
                date = date.split("Rated on ")[1]
                date = datetime.strptime(date, input_date_format).strftime(
                    output_date_format
                )
            else:
                date = datetime.today().strftime(output_date_format)
            captured_data.append({"id": imdb_id, "rating": rating, "date": date})
    except TimeoutError:
        pass

    context.close()
    browser.close()


def main(output: str, user_id: str = "ur9028759"):
    global captured_data
    captured_data = []
    with sync_playwright() as playwright:
        get_ratings(playwright, user_id=user_id)

    if len(captured_data) == 0:
        print("No data captured")
        return

    with open(output, "w") as f:
        json.dump(captured_data, f, indent=2)


if __name__ == "__main__":
    fire.Fire(main)
