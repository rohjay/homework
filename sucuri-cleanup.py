# So far I'm mainly trying to collect the bits of code that I'm going to need for the core functionality of the script
# this is by no means functional. And so far everything pretty much looks like a global. I'll work these bits down
# into functions as I go, at least that's the plan so far ;)

import sys
import os
import requests
import re
salts = requests.get('https://api.wordpress.org/secret-key/1.1/salt/').text.rstrip().split('\n')
pwd = os.getcwd()
install = pwd.split('/')[4]
def salt_replace():
    """
    Replace the salts in the installs wp-config.php file & grab the prefix while we're there.
    """
    regex_list=["AUTH_KEY","SECURE_AUTH_KEY","LOGGED_IN_KEY","NONCE_KEY","AUTH_SALT","SECURE_AUTH_SALT","LOGGED_IN_SALT","NONCE_SALT"]
    regex_prefix="\$table_prefix\s=\s\'(\w+_?)\';"
    regex_prefix=re.compile(regex_prefix)
    output=""
    #wp_config = open("/nas/content/live/"+ install + "/wp-config.php", "r+")
    wp_config = open("./wp-config.php", "r") #using this instead of an actual path for testing
    text = wp_config.read()
    wp_config.close()
    #os.rename("nas/content/live/"+ install + "/wp-config.php", "nas/content/live/" + install + "/wp-config-security_backup.php")
    os.rename("./wp-config.php", "./wp-config-security_backup.php")
    wp_config = open("./wp-config.php", "w")
    text=text.rstrip().split('\n')
    for index1,line in enumerate(text):
        for index2,match in enumerate(regex_list):
            print "index1= ", str(index1), "Text= ", line
            print "index2= ", str(index2), "Text=", match
            if re.search(match,line) != None:
                print "Presently writing ", salts[index2], "to line ", str(index1), "at position ", wp_config.tell(), "as matched by ", re.search(match,line)
                output=salts[index2]
        if output !="":
            wp_config.write(output)
            wp_config.write("\n")
            output=""
        else:
            wp_config.write(line)
            wp_config.write("\n")
    wp_config.close
print("Okay! running the replacer now!")
salt_replace()
