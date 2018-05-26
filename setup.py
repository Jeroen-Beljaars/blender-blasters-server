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
    run("apt-get install python-pip")
    run("pip3 install -r requirements.txt")

    # import the installed packages
    import requests
    from pynput.keyboard import Key, Controller
    
    ip = requests.get("http://ipecho.net/plain?").text
    network_config = {
        "local": False,
        "server_manager": True,
        "manager_ip": ip,
        "server_ip": ip
    }
    with open('network_config.json', 'w') as network_json:
        json.dump(network_config, network_json)
    
    run("sudo apt-get update")
    run("sudo apt-get install screen")
    run("screen")
    run("python3 manage_servers.py")

    keyboard = Controller()
    keyboard.press(Key.ctrl)
    keyboard.press('a')
    keyboard.release(Key.ctrl)
    keyboard.release('a')
    keyboard.press('d')
    os.system('echo the server is running you can close the terminal now')
