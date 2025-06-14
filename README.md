Who is GarfBot?
======
![garfield](https://www.crate.zip/garfield.png)

GarfBot is a discord bot that uses OpenAI's generative pre-trained models to produce text and images for your personal entertainment and companionship.
<br>There are a few ways you can interact with him on discord, either in a public server or by direct message:

`hey garfield {prompt}`
<br>Responds with text.

`garfpic {prompt}`
<br>Responds with an image.

`garfping {target}`
<br>Responds with iputils-ping result from target.

`garfdns {target}`
<br>Responds with dns lookup result from target.

`garfhack {target}`
<br>Responds with nmap scan result from target.

`garfshop {item} {zip}`
<br>Responds with 10 grocery {item}s from the nearest Kroger location, listed from least to most expensive.

`garfwiki {query}`
<br>Garfbot looks up a wikipedia article and will summarize it for you.

`garfqr {text}`
<br>Create a QR code for any string up to 1000 characters.

`garfbot response {add} {trigger} {response}`
<br>Add a GarfBot auto response for your server. Use "quotes" if you like.

`garfbot response {remove} {trigger}`
<br>Remove a GarfBot auto response for your server.

`garfbot response {list}`
<br>List current GarfBot auto responses for your server.

`garfbot help`
<br>Show a list of these commands.

Installation
======

To get started, clone this repo and create a config file.

```console
$ git clone https://git.crate.zip/crate/garfbot.git && cd garfbot/ && nano config.py
```

Add your various API tokens:

```python
GARFBOT_TOKEN = "Discord API token"
OPENAI_TOKEN = "OpenAI API token"
```

I recommend building a docker image using the included DockerFile as a template.
<br>Run the container binding /usr/src/app to GarfBot's CWD:

```console
$ docker build -t garfbot .
$ docker run -d --restart always -v $PWD:/usr/src/app --name garfbot garfbot
```

In case you'd rather not do it manually, a `garfbot.tf` file has been included to launch GarfBot and his friends' containers.

If you prefer to install dependencies on you own host and run as a systemd service:

```console
$ sudo nano /etc/systemd/system/garfbot.service
```

Replace $USER with your username:

```console
[Unit]
Description=garfbot
After=multi-user.target

[Service]
Type=simple
Restart=always
User=$USER
WorkingDirectory=/home/$USER/garfbot
ExecStart=/usr/bin/python garfbot.py

[Install]
WantedBy=multi-user.target
```

And finally:

```console
$ sudo systemctl daemon-reload
$ sudo systemctl enable garfbot
$ sudo systemctl start garfbot
```