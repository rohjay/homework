# So far I'm mainly trying to collect the bits of code that I'm going to need for the core functionality of the script
# this is by no means functional. And so far everything pretty much looks like a global. I'll work these bits down
# into functions as I go, at least that's the plan so far ;)

import sys
import os
import requests
import re
import _mysql as dbcon
debug = False
salts = requests.get('https://api.wordpress.org/secret-key/1.1/salt/').text.rstrip().split('\n')
pwd = os.getcwd()
install = pwd.split('/')[4]
def salt_replace():
    """
    Replace the salts in the installs wp-config.php file & grab the prefix while we're there.
    """
    regex_list=["AUTH_KEY","SECURE_AUTH_KEY","LOGGED_IN_KEY","NONCE_KEY","AUTH_SALT","SECURE_AUTH_SALT","LOGGED_IN_SALT","NONCE_SALT"]
    regex_prefix="\$table_prefix\s+=\s+\'(\w+_?)\';"
    regex_dbuser="define\(\s+\'DB_USER\',\s+\'(\w+)\'\s+\);"
    regex_dbpass="define\(\s+\'DB_PASSWORD\',\s+\'([A-Za-z0-9]+)\'\s+\);"
    regex_dbname="define\(\s+\'DB_NAME\',\s+\'(\w+)\'\s+\);"
    output=""
    wp_config = open("/nas/content/live/"+ install + "/wp-config.php", "r+")
    text = wp_config.read()
    wp_config.close()
    os.rename("nas/content/live/"+ install + "/wp-config.php", "nas/content/live/" + install + "/wp-config-security_backup.php")
    wp_config = open("./wp-config.php", "w")
    text=text.rstrip().split('\n')
    for index1,line in enumerate(text):
        for index2,match in enumerate(regex_list):
            if debug == True:
                print "index1= ", str(index1), "Text= ", line
                print "index2= ", str(index2), "Text=", match
            if re.search(match,line) != None:
                if debug == True: print "Presently writing ", salts[index2], "to line ", str(index1), "at position ", wp_config.tell(), "as matched by ", re.search(match,line)
                output=salts[index2]
        if output !="":
            wp_config.write(output)
            wp_config.write("\n")
            output=""
        else:
            wp_config.write(line)
            wp_config.write("\n")
        if re.search(regex_prefix,line) != None:
            prefix = re.search(regex_prefix,line).group(1)
        if re.search(regex_dbname,line) != None:
            dbname = re.search(regex_dbname,line).group(1)
        if re.search(regex_dbpass,line) != None:
            dbpass = re.search(regex_dbpass,line).group(1)
        if re.search(regex_dbuser,line) != None:
            dbuser = re.search(regex_dbuser,line).group(1)
    wp_config.close
    return str(prefix), str(dbname), str(dbpass), str(dbuser)
def reset_userkeys(dbvalues):
    """
    Reset user activation keys in the DB to prevent password stealing
    """
    db=dbcon.connect("localhost",dbvalues[3],dbvalues[2],dbvalues[1])
    db.query("update " + dbvalues[0] + "users set user_activation_key='';")
    r=db.affected_rows()
    return int(r)
print("Replacing Security salts now...")
dbvalues = salt_replace()
print "Salts updated. Backup file made"
if debug == True:
    print "prefix: '", dbvalues[0], "'"
    print "dbname: '", dbvalues[1], "'"
    print "dbpass: '", dbvalues[2], "'"
    print "dbuser: '", dbvalues[3], "'"
result = reset_userkeys(dbvalues)
print "successfully reset user activation keys. Updated "+ str(result) + " rows"
print "Turning off theme editor:"
theme_editor=os.system('php /nas/wp/www/tools/wpe.php option-set '+install+' allow_theme_editor []')
print "Creating backup point:"
os.system('snappyshot snapshot:create /nas/content/live/'+install+' '+install+'-live "Cleaned Site: WPE"')
