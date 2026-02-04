FROM python:slim

RUN pip install playwright fire
RUN playwright install --with-deps chromium-headless-shell

WORKDIR /app
COPY *.py /app

ENTRYPOINT ["python"]
