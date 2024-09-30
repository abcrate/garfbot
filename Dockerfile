FROM python:3.11-bookworm⁠

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN apt update
RUN apt install -y nmap
# RUN apt install -y rustc
RUN apt install -y python3
RUN apt install -y python3-pip
# RUN pip3 install --no-cache-dir -r requirements.txt -vvv
RUN pip3 install discord
RUN pip3 install openai
RUN pip3 install aiohttp
RUN pip3 install requests

CMD [ "python", "./garfbot.py" ]
