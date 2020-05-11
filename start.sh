#!/bin/bash
bash /var/www/march-madness-back/install.sh
source /var/www/march-madness-back/march-madness-back-env/bin/activate
python3 /var/www/march-madness-back/api.py