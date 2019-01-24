#Method for getting credentials from a given directory
import re

def getcreds(location):
    if location is None:
        print("Please give a credentials file location")
        return None,None
    f = open(location, "rb")
    for line in f:
        if "username" in line:
            user = re.sub("username ", "", line)
            user=user.rstrip()
        if "password" in line:
            pwd = re.sub("password ", "", line)
            pwd=pwd.rstrip()
    return user, pwd


