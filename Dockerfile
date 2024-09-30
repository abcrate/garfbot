FROM python:3.13.0rc2-bookworm

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN apt update
RUN apt install nmap -y
RUN pip install --no-cache-dir -r requirements.txt -vvv

CMD [ "python", "./garfbot.py" ]
