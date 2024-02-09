FROM python:3.10

WORKDIR /app
COPY fetch_pubs.py requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

CMD ["/usr/local/bin/python3", "fetch_pubs.py"]