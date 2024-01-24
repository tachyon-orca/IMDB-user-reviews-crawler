FROM python:slim
RUN pip install scrapy
WORKDIR /app
COPY . /app
ENTRYPOINT ["scrapy", "crawl"]
