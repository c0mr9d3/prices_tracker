#!/bin/sh

/etc/init.d/nginx start
cd /home/$1/prices_tracker/web_app
uid=`id -u $1`
uwsgi --uid $uid --ini uwsgi.ini
