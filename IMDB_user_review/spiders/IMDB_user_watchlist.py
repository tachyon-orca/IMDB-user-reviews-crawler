import json
import re
from datetime import datetime
import scrapy


class IMDBUserWatchlist(scrapy.Spider):
    name = "watchlist"

    def start_requests(self):
        userid = self.settings.get("userid", "ur9028759")
        url = f"https://www.imdb.com/user/{userid}/watchlist"
        yield scrapy.Request(url, self.parse)

    @classmethod
    def update_settings(self, settings):
        super().update_settings(settings)

    def parse(self, response):
        data = re.findall(
            r"IMDbReactInitialState.push\((.+)\);", response.body.decode()
        )
        data = json.loads(data[0])
        for movie in data["list"]["items"]:
            yield {"id": movie["const"], "date": movie["added"]}
