FROM python:3.12.4

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./static /code/static
COPY ./templates /code/templates

RUN export WORKERS=$(nproc) && \
    echo "Number of workers set to: $WORKERS"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --loop uvloop --http h11 --workers $WORKERS"]
