#!/bin/bash
set -e

find /tmp/navpage/icons -type f > /tmp/navpage/icons.txt
#cat /tmp/update_hosts.sh.txt | tee /tmp/update_hosts.sh > /dev/null
#python3 /tmp/navpage/private_html/rss_news.py >> /tmp/logs/rss_news.log 2>&1
python3 /tmp/navpage/private_html/private_html/generate_portal_config_mulu.py >> /tmp/logs/gen_private_html.log 2>&1
