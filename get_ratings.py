import json
import re

import fire
from playwright.sync_api import Playwright, TimeoutError, sync_playwright


def intercept_response(response):
    global captured_data
    if "api.graphql.imdb.com" in response.url:
        request = response.request.post_data_json
        if (
            request is not None
            and request.get("operationName") == "UserRatingsAndWatchOptions"
        ):
            try:
                json_data = response.json()
                captured_data.append(json_data)
                print(f"Captured JSON data from: {response.url}")
            except:
                print(f"Failed to capture JSON from: {response.url}")
    return response


def get_ratings(playwright: Playwright, user_id: str) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.on("response", intercept_response)
    try:
        page.goto(f"https://www.imdb.com/user/{user_id}/ratings")
        page.wait_for_load_state("networkidle")
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

    extracted_ratings = []
    ratings = captured_data[0]
    for title in ratings["data"]["titles"]:
        rating = title["otherUserRating"]
        extracted_ratings.append(
            {
                "id": title["id"],
                "rating": str(rating["value"]),
                "date": re.findall(r"\d{4}-\d{2}-\d{2}", rating["date"])[0],
            }
        )

    with open(output, "w") as f:
        json.dump(extracted_ratings, f, indent=2)


if __name__ == "__main__":
    fire.Fire(main)
