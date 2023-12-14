FROM python:3.9

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:80", "foodgram.wsgi"]