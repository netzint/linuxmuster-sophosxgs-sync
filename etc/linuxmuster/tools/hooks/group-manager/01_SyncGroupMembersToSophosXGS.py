#!/usr/bin/env python3

#######################################################
#
#  Netzint GmbH 2024
#  lukas.spitznagel@netzint.de
#  https://github.com/hermanntoast
#
#######################################################

import os
import yaml
import sys
import time

from sophosxgs import SophosAPI, SophosAPIType, SophosAPIType_UserStatus

def readConfigFile(school: str = ""):
    configStr = "/etc/linuxmuster/sophos/"
    if school == "":
        configStr += "config.yml"
    else:
        configStr += f"{school}.config.yml"
        
    try:
        with open("/etc/linuxmuster/sophos/config.yml", "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print("ERROR: Could not load config! " + str(e))

def getSambaDomain():
    with open("/var/lib/linuxmuster/setup.ini") as f:
        for line in f.readlines():
            if "domainname" in line:
                return line.split("=")[1].strip()
    return "linuxmuster.lan"

def main():
    parameters = sys.argv
    if len(parameters) == 4:
        action = parameters[1]
        groupname = parameters[2]
        users = parameters[3]
    else:
        print("ERROR: Not enought parameters given!")
        print("./01_SyncGroupMembersToSophosXGS.py <ADD/REMOVE> <GROUPNAME> <USER(s)>")
        exit(1)

    if "," in users:
        users = users.split(",")
    else:
        users = [users]

    if "-" in groupname:
        school = groupname.split("-", 1)[0]
        config = readConfigFile(school)
    else:
        config = readConfigFile()
        
    sambadomain = getSambaDomain()

    api = SophosAPI(config["url"], config["port"], config["username"], config["password"])

    for user in users:
        userlist = [user + "@" + sambadomain]
        api.toggle(SophosAPIType.USERSTATUS, SophosAPIType_UserStatus(SophosAPIType_UserStatus.USERSTATUS_DEACTIVATE, userlist), SophosAPIType_UserStatus(SophosAPIType_UserStatus.USERSTATUS_ACTIVATE, userlist))
        print(f"Successfully toggled users '{userlist[0]}'!")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("\n --- %s seconds ---" % (time.time() - start_time))
