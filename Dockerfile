FROM python:slim
RUN pip install playwright fire
RUN playwright install --with-deps
WORKDIR /app
COPY *.py /app
ENTRYPOINT ["python"]
