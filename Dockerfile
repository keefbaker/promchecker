FROM python:3

COPY requirements.txt requirements.txt
COPY source/* .

RUN python -m pip install -r requirements.txt
ENTRYPOINT [ "python", "promcheck.py" ]