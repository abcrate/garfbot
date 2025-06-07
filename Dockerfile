FROM python:alpine
WORKDIR /usr/src/app

RUN apk update && \
    apk add --no-cache \
    iputils \
    bind-tools \
    nmap \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev

RUN pip3 install --no-cache-dir \
    discord \
    openai \
    aiohttp \
    requests \
    wikipedia \
    pillow \
    qrcode

CMD [ "python", "garfmain.py" ]