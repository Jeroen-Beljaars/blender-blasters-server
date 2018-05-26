import os
import sys
import json
from time import sleep

operating_system = sys.platform
if 'win' in operating_system:
    print("Sorry setup.py is not supported on windows\n" \
          "the server is ment to run on a linux server!")
elif 'linux' in operating_system:
    os.system("apt-get install python-pip")
    sleep(3)
    os.system("pip3 install -r requirements.txt")
    sleep(7)

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
    os.system("sudo apt-get update")
    sleep(30)
    os.system("sudo apt-get install screen")
    sleep(10)
    os.system("screen")
    sleep(2)
    os.system("python3 manage_servers.py")
    sleep(1)
    keyboard = Controller()
    keyboard.press(Key.ctrl)
    keyboard.press('a')
    keyboard.release(Key.ctrl)
    keyboard.release('a')
    keyboard.press('d')
    os.system('echo the server is running you can close the terminal now')
