GarfBot is a discord bot that uses openai generative pre-trained AI models to produce text and images for your personal entertainment and companionship.


To interact: (not case-sensitive)

`"hey garfield"`
    responds with text.

`"garfpic"`
    responds with image.


To get started, clone this repo and create a `config.py` file in GarfBot's root directory. Open your favorite text editor or IDE and add your various API tokens as such:

```python
GARFBOT_TOKEN = "token"
OPENAI_TOKEN = "token"
GIF_TOKEN = "token"
```
If you want to configure a more secure setup, go ahead.

Next, I recommend building a docker image for each bot using the included DockerFile as a template. Run each container binding /usr/src/app to GarfBot's CWD.

A terraform file has been included to launch all three containers, or you can do it manually.

Example:
```console
crate@raspberrypi:~/garfbot $ docker build -t garfbot .
crate@raspberrypi:~/garfbot $ docker run -d --restart always -v $PWD:/usr/src/app --name garfbot garfbot
```

Or if you prefer to install dependencies (from requirements.txt) on you own host and run as a systemd service:
```console
[Unit]
Description=garfbot
After=multi-user.target

[Service]
Type=simple
Restart=always
User=pi
WorkingDirectory=/home/crate/garfbot
ExecStart=/usr/bin/python ./garfbot.py

[Install]
WantedBy=multi-user.target
```
