import csv
import json
import re

import fire
from playwright.sync_api import Playwright, TimeoutError, sync_playwright


def download_watchlist(playwright: Playwright, user_id: str) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto(f"https://www.imdb.com/user/{user_id}/watchlist")
    page.get_by_label("Export").click(timeout=60000)
    page.goto("https://www.imdb.com/exports/")
    while True:
        try:
            with page.expect_download() as download_info:
                locator = page.get_by_test_id("export-status-button")
                if not re.match(r"Ready.*", locator.inner_text(timeout=5000)):
                    page.reload()
                    continue
                locator.click()
                break
        except TimeoutError:
            page.reload(timeout=90000)
    download = download_info.value
    download.save_as("watchlist.csv")

    context.close()
    browser.close()


def main(output: str, user_id: str = "ur9028759"):
    with sync_playwright() as playwright:
        download_watchlist(playwright, user_id=user_id)
    with open("watchlist.csv", newline="") as f:
        reader = csv.reader(f)
        watchlist = []
        next(reader)
        for row in reader:
            watchlist.append({"id": row[1], "date": row[2]})
    with open(output, "w") as f:
        json.dump(watchlist, f, indent=2)


if __name__ == "__main__":
    fire.Fire(main)
