import os
import sys
import json
from time import sleep
from subprocess import run

operating_system = sys.platform
if 'win' in operating_system:
    print("Sorry setup.py is not supported on windows\n" \
          "the server is ment to run on a linux server!")
elif 'linux' in operating_system:
    run("sudo apt-get update && sudo apt-get -y upgrade", shell=True)
    run("sudo apt-get install python3-pip", shell=True)
    run("pip3 install -r requirements.txt", shell=True)

    # import the installed packages
    import requests
    
    ip = requests.get("http://ipecho.net/plain?").text
    network_config = {
        "local": False,
        "server_manager": True,
        "manager_ip": ip,
        "server_ip": ip
    }
    with open('network_config.json', 'w') as network_json:
        json.dump(network_config, network_json)
    
    run("sudo apt-get update", shell=True)
    run("sudo apt-get install screen", shell=True)
    run("screen", shell=True)
