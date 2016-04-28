#ITS ALIVE!!!!!!!
#And now, it's also more optimized. We've removed the nested for looping, and made some other minor enhancements.
#The script now also checks to see if it's being run from an install's folder, and if not, it fails out with debug
#Command line options for debug output and executing from a local command prompt have been added to streamline future additions to the code
#did some cleanup to make the code prettier, and hopefully easier to read.

import sys
import os
import requests
import re
import _mysql as dbcon
debug = False
local = False
salts = requests.get('https://api.wordpress.org/secret-key/1.1/salt/').text
pwd = os.getcwd()
install = pwd.split('/')[4]
install_type = pwd.split('/')[3]
def salt_replace():
    """
    Replace the salts in the installs wp-config.php file & grab the prefix while we're there.
    """
    salt_regex=re.compile("^define\('(AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY|AUTH_SALT|SECURE_AUTH_SALT|LOGGED_IN_SALT|NONCE_SALT).*$")
    regex_prefix=re.compile("\$table_prefix\s+=\s+\'(\w+_?)\';")
    regex_dbuser=re.compile("define\(\s+\'DB_USER\',\s+\'(\w+)\'\s+\);")
    regex_dbpass=re.compile("define\(\s+\'DB_PASSWORD\',\s+\'([A-Za-z0-9]+)\'\s+\);")
    regex_dbname=re.compile("define\(\s+\'DB_NAME\',\s+\'(\w+)\'\s+\);")
    output=""
    os.rename("./wp-config.php", "./wp-config-security_backup.php")
    with open("./wp-config-security_backup.php", "r+") as thing:
        text = thing.read()
    wp_config = open("./wp-config.php", "w")
    text=text.rstrip().split('\n')
    for index1,line in enumerate(text):
        if re.search(salt_regex,line) != None:
            match=re.search(salt_regex,line).group(1)
            if debug == True:
                print "match= ", match
                print "salts=", salts
            output=re.search("define\('"+match+".*",salts).group()
        if output != "":
            wp_config.write(output)
            wp_config.write("\n")
            output=""
            if debug == True:
                print "Presently writing ", output, "to line ", str(index1), "at position ", wp_config.tell(), "as matched by ", re.search(salt_regex,line)
        else:
            if debug == True:
                print "no match on this line! Writing ", line, "to line", str(index1), "at position", wp_config.tell()
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
    try:
        db=dbcon.connect("localhost",dbvalues[3],dbvalues[2],dbvalues[1])
        db.query("update " + dbvalues[0] + "users set user_activation_key='';")
        r=db.affected_rows()
        return int(r)
    except:
        print "Uh-ohs! Looks like something bad happened while trying to connect to the DB :("
        print "Here's everything we know:"
        print "prefix: '", dbvalues[0], "'"
        print "dbname: '", dbvalues[1], "'"
        print "dbpass: '", dbvalues[2], "'"
        print "dbuser: '", dbvalues[3], "'"
        print "This can usually be fixed with an apply."
def sanity_checks():
    try:
        if str(sys.argv[1]) == "debug":
            global debug
            debug = True
    except:
        pass
    try:
        if str(sys.argv[2]) == "local":
            global local
            local = True
    except:
        pass
    if local == True:
        pass
    elif install_type not in ("live", "staging"):
        print "Oh noes! You have to run me from an install's folder!"
        sys.exit()

sanity_checks()
print("Replacing Security salts now...")
dbvalues = salt_replace()
print "Salts updated. Backup file made"
if debug == True:
    print "prefix: '", dbvalues[0], "'"
    print "dbname: '", dbvalues[1], "'"
    print "dbpass: '", dbvalues[2], "'"
    print "dbuser: '", dbvalues[3], "'"
if local != True:
    result = reset_userkeys(dbvalues)
    print "successfully reset user activation keys. Updated "+ str(result) + " rows"
    print "Turning off theme editor:"
    theme_editor=os.system('php /nas/wp/www/tools/wpe.php option-set '+install+' allow_theme_editor []')
    print "Creating backup point:"
    os.system('snappyshot snapshot:create ' + pwd +' ' + install+'-'+install_type+ ' "Cleaned Site: WPE"')
else:
    print "Running locally. Not resetting keys, modifying theme editor, or making backup. These can only be done on the server"
    sys.exit()
