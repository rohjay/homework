# So far I'm mainly trying to collect the bits of code that I'm going to need for the core functionality of the script
# this is by no means functional. And so far everything pretty much looks like a global. I'll work these bits down
# into functions as I go, at least that's the plan so far ;)

import sys
import os
import requests
import re

salts = requests.get('https://api.wordpress.org/secret-key/1.1/salt/')
pwd = os.getcwd()
install = pwd.split('/')[4]

def salt_replace()
    """
    Replace the salts in the installs wp-config.php file & grab the prefix while we're there.
    """
    wp_config = open("/nas/content/live/"+ install + "/wp-config.php", r+)
    for line in wp_config:
        
