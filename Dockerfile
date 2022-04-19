FROM python:3

COPY requirements.txt requirements.txt
COPY source/* .
RUN apt update && apt upgrade -y && apt clean all && \
     python -m pip install -r requirements.txt && \
     useradd bob
USER bob
ENTRYPOINT [ "python", "promcheck.py" ]