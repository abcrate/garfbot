Who is GarfBot?
======

GarfBot is a discord bot that uses openai generative pre-trained AI models to produce text and images for your personal entertainment and companionship. There are a few ways you can interact with him on discord, either in a server you've invited him to or by direct message:

`hey garfield {prompt}`
Responds with text.

`garfpic {prompt}`
Responds with an image.

`garfping {target}`
Responds with iputils-ping result from target.

`garfpic {target}`
Responds with dnsutils lookup result from target.

`garfpic {target}`
Responds with nmap scan result from target.

`garfshop {item} {zip}`
Responds with 10 grocery {item}s from the nearest Kroger location, listed from least to most expensive.

Installation
======

To get started, `git clone https://git.crate.zip/crate/garfbot.git` and create a `config.py` file in the root directory.
Open your favorite text editor and add your various API tokens:

```python
GARFBOT_TOKEN = "Discord API token"
OPENAI_TOKEN = "OpenAI API token"
GIF_TOKEN = "tenor.com API token"
```

I recommend building a docker image using the included DockerFile as a template. Run the container binding /usr/src/app to GarfBot's CWD:

```console
crate@raspberrypi:~/garfbot $ docker build -t garfbot .
crate@raspberrypi:~/garfbot $ docker run -d --restart always -v $PWD:/usr/src/app --name garfbot garfbot
```
In case you'd rather not do it manually, a `garfbot.tf` file has been included to launch GarfBot and his friends' containers.

If you prefer to install dependencies on you own host and run as a systemd service:

```console
crate@raspberrypi:~/garfbot $ sudo nano /etc/systemd/system/garfbot.service
```
Replace {user} with your username:
```console
[Unit]
Description=garfbot
After=multi-user.target

[Service]
Type=simple
Restart=always
User={user}
WorkingDirectory=/home/{user}/garfbot
ExecStart=/usr/bin/python garfbot.py

[Install]
WantedBy=multi-user.target
```
And finally:
```console
crate@raspberrypi:~/garfbot $ sudo systemctl daemon-reload
crate@raspberrypi:~/garfbot $ sudo systemctl enable garfbot
crate@raspberrypi:~/garfbot $ sudo systemctl start garfbot
```