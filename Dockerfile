FROM python:3.11.10-bookworm

WORKDIR /usr/src/app

RUN apt update
RUN apt install -y iputils-ping
RUN apt install -y dnsutils
RUN apt install -y nmap
RUN apt install -y python3
RUN apt install -y python3-pip
RUN pip3 install discord
RUN pip3 install openai
RUN pip3 install aiohttp
RUN pip3 install requests

CMD [ "python", "./garfbot.py" ]
