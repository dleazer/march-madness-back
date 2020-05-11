#!/bin/bash
if [[ ! -d /var/www/march-madness-back/march-madness-back-env ]]
then
    apt update
    apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv
    python3 -m venv /var/www/march-madness-back/march-madness-back-env
    source /var/www/march-madness-back/march-madness-back-env/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r /var/www/march-madness-back/requirements.txt
    deactivate
fi