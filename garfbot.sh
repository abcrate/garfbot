#!/bin/bash

docker run -d --restart always -v $PWD:/usr/src/app --name garfbot garfbot
