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
#import threading
import time

from cryptography.fernet import Fernet
from sophosxgs import SophosAPI, SophosAPIType, SophosAPIType_User, SophosAPIType_LiveUserLogin, SophosAPIType_LiveUserLogout, SophosAPIType_UserStatus

# XGS_FALLBACK_GROUP = "Open Group"
# LMN_GROUP_PREFIX = "lmn-auto-"

def readConfigFile():
    try:
        with open("/etc/linuxmuster/sophos/config.yml", "r") as f:
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

def getSambaDomain():
    with open("/var/lib/linuxmuster/setup.ini") as f:
        for line in f.readlines():
            if "domainname" in line:
                return line.split("=")[1].strip()
    return "linuxmuster.lan"

# def createUserObjectOnXGS(api, username, action, group):
#     res = api.request(SophosAPIType.LIVEUSERLOGIN, SophosAPIType_LiveUserLogin(username, "1.2.3.4"))
#     if res.getStatus():
#         print(f"[{username}] Live-Login successful!")
#         res = api.request(SophosAPIType.LIVEUSERLOGOUT, SophosAPIType_LiveUserLogout(username, "1.2.3.4"))
#         if res.getStatus():
#             print(f"[{username}] Live-Logout successful!")
#         else:
#             print(f"[{username}] Live-Logout failed! That's no problem. You can ignore that ;-)")

#         if action == "add":
#             res = api.update(SophosAPIType.USER, SophosAPIType_User(username, username, group))
#             if res.getStatus():
#                 print(f"[{username}] User '{username}' successfully added to group '{group}'")
#             else:
#                 print(f"[{username}] [ERROR] Could not add user '{username}' to group '{group}'")
#         elif action == "remove":
#             res = api.update(SophosAPIType.USER, SophosAPIType_User(username, username, XGS_FALLBACK_GROUP))
#             if res.getStatus():
#                 print(f"[{username}] User '{username}' successfully removed from group '{group}'")
#             else:
#                 print(f"[{username}] [ERROR] Could not remove user '{username}' from group '{group}'")
#     else:
#         print(f"[{username}] Live-Login failed!")

def deactivateUsersOnXGS(api, users):
    res = api.set(SophosAPIType.USERSTATUS, SophosAPIType_UserStatus(SophosAPIType_UserStatus.USERSTATUS_DEACTIVATE, users))
    if res.getStatus():
        print("Successfully deactivate user(s)!")
    else:
        print("Failed to deactivate user(s)!")



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

    config = readConfigFile()
    sambadomain = getSambaDomain()

    userlist = []
    for user in users:
        userlist.append(user + "@" + sambadomain)

    api = SophosAPI(config["url"], config["port"], config["username"], decryptPassword(config["password"]))
    deactivateUsersOnXGS(api, userlist)

    # group_list = []
    # groups = api.get(SophosAPIType.USERGROUP)
    # for group in groups.get()["GroupDetail"]:
    #     group_list.append(group["Name"])

    # if LMN_GROUP_PREFIX + groupname in group_list:
    #     if action == "add":
    #         for user in users:
    #             res = api.update(SophosAPIType.USER, SophosAPIType_User(user + "@" + sambadomain, user + "@" + sambadomain, LMN_GROUP_PREFIX + groupname))
    #             if res.getStatus():
    #                 print(f"User '{user}' successfully added to group '{LMN_GROUP_PREFIX + groupname}'")
    #             else:
    #                 print(f"[ERROR] Could not add user '{user}' to group '{LMN_GROUP_PREFIX + groupname}'. Try to create user on firewall... -> [BACKGROUND-TASK]")
    #                 threading.Thread(target=createUserObjectOnXGS, args=(api, user + "@" + sambadomain, action, LMN_GROUP_PREFIX + groupname)).start()
    #     elif action == "remove":
    #         for user in users:
    #             if LMN_GROUP_PREFIX + "no" + groupname in group_list:
    #                 res = api.update(SophosAPIType.USER, SophosAPIType_User(user + "@" + sambadomain, user + "@" + sambadomain, LMN_GROUP_PREFIX + "no" + groupname))
    #             else:
    #                 res = api.update(SophosAPIType.USER, SophosAPIType_User(user + "@" + sambadomain, user + "@" + sambadomain, XGS_FALLBACK_GROUP))
    #             if res.getStatus():
    #                 print(f"User '{user}' successfully removed from group '{LMN_GROUP_PREFIX + groupname}'")
    #             else:
    #                 print(f"[ERROR] Could not remove user '{user}' from group '{LMN_GROUP_PREFIX + groupname}'. Try to create user on firewall... -> [BACKGROUND-TASK]")
    #                 threading.Thread(target=createUserObjectOnXGS, args=(api, user + "@" + sambadomain, action, LMN_GROUP_PREFIX + groupname)).start()
    #     else:
    #         print(f"Unknown action '{action}'!")
    # else:
    #     print(f"Group does not exist! Please create a new group '{LMN_GROUP_PREFIX + groupname}' on your XGS-Firewall!")



if __name__ == "__main__":
    start_time = time.time()
    main()
    print("\n --- %s seconds ---" % (time.time() - start_time))