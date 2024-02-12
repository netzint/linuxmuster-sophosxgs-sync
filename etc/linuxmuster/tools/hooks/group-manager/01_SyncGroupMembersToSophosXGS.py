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
import base64
import sys

from cryptography.fernet import Fernet
from sophosxgs import SophosAPI, SophosAPIType, SophosAPIType_User

GROUPNAME_PREFIX = "lmn-auto-"
XGS_FALLBACK_GROUP = "Open Group"

def readConfigFile():
    try:
        with open("/etc/linuxmuster/tools/linuxmuster-sophosxgs-sync/config.yml", "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print("ERROR: Could not load config! " + str(e))

def decryptPassword(password):
    try:
        with open("/etc/machine-id", "r") as f:
            crypt = Fernet(base64.urlsafe_b64encode(f.read().replace("\n", "").encode()))
            return crypt.decrypt(password).decode()
    except Exception as e:
        print("ERROR: Failed to decrypt password in config! " + str(e))


def main():
    parameters = sys.argv
    if len(parameters) == 4:
        action = parameters[1]
        groupname = parameters[2]
        users = parameters[3]
    else:
        print("ERROR: Not enought parameters given!")
        exit(1)

    if "," in users:
        users = users.split(",")
    else:
        users = [users]

    config = readConfigFile()

    api = SophosAPI(config["url"], config["port"], config["username"], decryptPassword(config["password"]))

    group_list = []
    groups = api.get(SophosAPIType.USERGROUP)
    if groups.getStatus()
        for group in groups.get()["GroupDetail"]:
            group_list.append(group["Name"].replace(GROUPNAME_PREFIX, ""))
    else:
        print("ERROR: Could not connect to XGS-Firewall. Please check credentials or firewall settings!")

    if groupname in group_list:
        if action == "add":
            for user in users:
                res = api.update(SophosAPIType.USER, SophosAPIType_User(user, user, GROUPNAME_PREFIX + groupname))
                if res.getStatus():
                    print(f"User '{user}' successfully added to group '{GROUPNAME_PREFIX + groupname}'")
                else:
                    print(f"[ERROR] Could not add user '{user}' to group '{GROUPNAME_PREFIX + groupname}'")
        elif action == "remove":
            for user in users:
                res = api.update(SophosAPIType.USER, SophosAPIType_User(user, user, XGS_FALLBACK_GROUP))
                if res.getStatus():
                    print(f"User '{user}' successfully removed from group '{GROUPNAME_PREFIX + groupname}'")
                else:
                    print(f"[ERROR] Could not remove user '{user}' from group '{GROUPNAME_PREFIX + groupname}'")
        else:
            print(f"Unknown action '{action}'!")
    else:
        print(f"Group does not exist! Please create a new group '{GROUPNAME_PREFIX + groupname}' on your XGS-Firewall!")



if __name__ == "__main__":
    main()