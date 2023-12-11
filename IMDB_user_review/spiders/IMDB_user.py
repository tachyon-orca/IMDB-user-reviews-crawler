from datetime import datetime
import scrapy


class IMDBUser(scrapy.Spider):
    name = "imdb"

    def start_requests(self):
        userid = self.settings.get("userid", "ur9028759")
        url = f"https://www.imdb.com/user/{userid}/ratings"
        yield scrapy.Request(url, self.parse)

    @classmethod
    def update_settings(self, settings):
        super().update_settings(settings)

    def parse(self, response):
        for movie in response.css("div.lister-item-content"):
            imdb_id = movie.css('div.wtw-option-standalone::attr(data-tconst)').get()
            rating = movie.css("div.ipl-rating-star--other-user span.ipl-rating-star__rating::text").get().strip()
            time = movie.xpath("./*[starts-with(text(), 'Rated on ')]/text()").get().strip()[9:]
            time = datetime.strptime(time, "%d %b %Y").strftime("%Y-%m-%d")
            yield {"id": imdb_id, "date": time, "rating": rating}

        next_page = response.css("a.next-page::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)