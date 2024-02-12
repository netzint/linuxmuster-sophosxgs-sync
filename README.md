# LINUXMUSTER SOPHOS-XGS Sync Group-Members

1. Edit config-file: /etc/linuxmuster/sophos/config.yml
    - Encrypt firewall-password with this tool: /usr/lib/python3/dist-packages/sophosxgs/generateSafePassword.py --password <PASSWORD>
2. Allow "Administration > Device-Access" from Server to Admin-Service-HTTPs
3. Activate API and allow Server-IP under "Backup & Firmware > API"
4. Import groups from linuxmuster via "Import Group Wizard"