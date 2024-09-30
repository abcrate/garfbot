FROM python:3.13.0rc2-bookworm

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN apt update
RUN apt install nmap -y
RUN apt install -y python3 python3-pip
# RUN pip3 install --no-cache-dir -r requirements.txt -vvv
RUN pip3 install discord
RUN pip3 install openai
RUN pip3 install aiohttp
RUN pip3 install requests

CMD [ "python", "./garfbot.py" ]
