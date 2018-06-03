import socket
import threading
import json
import time
import traceback
import re
import sys
import os
from random import randint
from os import getcwd

# [i] is ene informatie bericht
# [!] is een error of een waarschuwing
# [+] Is een nieuwe connectie
# [-] Is een afgesloten connectie

with open("network_config.json") as file:
    network_config = json.load(file)

class Server:
    def __init__(self, config, matches):
        """ Initialize the server """
        self.matches = matches
        self.config = config
        print(self.config)
        # The ip of the machine where the server is running on
        self.bind_ip = network_config['server_ip'] # IP OF THE SERVER

        # UDP Server - For less important packets like worldpos
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if network_config['server_manager']:
            self.server.bind((self.bind_ip, 0))
        else:
            self.server.bind((self.bind_ip, 9999))

        self.bind_port = self.server.getsockname()[1]

        # Store the user_addresses here
        self.user_addresses = {}

        self.client_id = 1

        print("[i] Started listening on {}:{}".format(self.bind_ip, self.bind_port))

        self.newcomer = ""

        self.latest_pos = {"init_connection": {}}
        self.position = {"position": {}}

        self.active_players = {}
        self.teams = {
            'team1': [],
            'team2': []
        }

        if network_config['server_manager']:
            manager = threading.Thread(target=self.manager_communication)
            manager.start()

        send = threading.Thread(target=self.sender)
        send.start()

        check_connection = threading.Thread(target=self.check_connection)
        check_connection.start()

        spawn_powerups = threading.Thread(target=self.spawn_powerups)
        spawn_powerups.start()

        self.handle_client()

    def manager_communication(self):
        manager_ip = network_config['manager_ip']
        manager_port = 9998
        manager_ip_port = "{}:{}".format(manager_ip, manager_port)

        manager = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        manager.connect((manager_ip, manager_port))

        inform_packet = {
            "new_server": {
                "ip_port": "{}:{}".format(self.bind_ip, self.bind_port),
                "ip": self.bind_ip,
                "port": self.bind_port
            }
        }

        manager.sendall(json.dumps(inform_packet).encode())

        power = threading.Thread(target=self.server_power, args=(manager,))
        power.start()

    def handle_client(self):
        """
        Every client has an own handler
        this method listens for incoming messages from a specific client
        """
        while True:
            try:
                # listen for packets
                try:
                    request, addr = self.server.recvfrom(1024)
                    self.active_players[addr] = True

                    if(addr not in self.user_addresses.values()):
                        self.handle_new_user_connection(request, addr)

                    try:
                        decoded_request = json.loads(request.decode())
                    except:
                        # not a json
                        decoded_request = {'unknown_message': 'ignore'}

                    if 'position' in decoded_request.keys():
                        self.latest_pos['init_connection']["{}:{}".format(addr[0],addr[1])]['position'] = decoded_request['position']['coordinates']
                        self.position['position']["{}:{}".format(addr[0], addr[1])] = decoded_request['position']['coordinates']
                    if 'shoot' in decoded_request.keys():
                        # Stuur het pakketje door naar de clients
                        self.broadcast_message(request)
                except:
                    pass
            except socket.error:
                # Socket error usally means that the client is not connected anymore
                # Disconnect it
                try:
                    self.user_addresses.pop(addr)
                    print(addr)
                except:
                    # If disconnecting failed then the user is allready disconnected elsewhere
                    pass

    def handle_new_user_connection(self, packet, addr):
        print("[+] Accepted connection from {}:{}".format(addr[0], addr[1]))
        print("[+] Establishing a connection form: {}:{}".format(addr[0], addr[1]))
        # add the user to the client list
        self.user_addresses["{}:{}".format(addr[0], addr[1])] = addr

        if len(self.user_addresses.keys()) > 1:
            self.server.sendto(json.dumps(self.latest_pos).encode(), addr)

        t1 = len(self.teams['team1'])
        t2 = len(self.teams['team2'])

        self.latest_pos['init_connection']["{}:{}".format(addr[0], addr[1])] = {}
        if t1 > t2:
            team = "team2"
            self.teams['team2'].append("{}:{}".format(addr[0], addr[1]))
        elif t2 > t1:
            team = "team1"
            self.teams['team1'].append("{}:{}".format(addr[0], addr[1]))
        else:
            team = 'team{}'.format(randint(1,2))
            self.teams[team].append("{}:{}".format(addr[0], addr[1]))
        self.latest_pos['init_connection']["{}:{}".format(addr[0], addr[1])]['team'] = team

        self.broadcast_new_connection("{}:{}".format(addr[0], addr[1]), team)

    def broadcast_new_connection(self, ip, team):
        """" If a player joins the game then broadcast it to all the clients """
        new_connection = {
            'new-connection': {
                'ip': ip,
                'object': 'Tank',
                'team': team,
                'config': self.config,
                'matches': self.matches,
            }
        }

        for client in self.user_addresses.values():
            self.server.sendto(json.dumps(new_connection).encode(), (client[0], client[1]))

    def broadcast_message(self, packet):
        """" Broadcast the message to all the clients """
        try:
            for client in self.user_addresses.values():
                self.server.sendto(packet, (client[0], client[1]))
        except RuntimeError:
            pass

    def sender(self):
        previous = []
        while True:
            if self.position['position'] != previous and len(self.position['position']):
                self.broadcast_message(json.dumps(self.position).encode())
                previous = self.position
                time.sleep(0.02)

    def check_connection(self):
        while True:
            for player in self.active_players.keys():
                self.active_players[player] = False
            time.sleep(1)
            try:
                for player in self.active_players.keys():
                    if not self.active_players[player]:
                        self.server.sendto(json.dumps({'ping': 'sendpong'}).encode(), player)
                        time.sleep(1)
                        if not self.active_players[player]:
                            try:
                                ip = "{}:{}".format(player[0], player[1])
                                self.latest_pos['init_connection'].pop(ip)
                                self.position['position'].pop(ip)
                                self.user_addresses.pop(ip)
                                self.active_players.pop(player)
                                print("[-] Client {} disconnected".format(ip))
                                self.broadcast_message(json.dumps({"disconnect": {"ip": ip}}).encode())
                            except KeyError:
                                pass
            except RuntimeError:
                pass

    def server_power(self, manager):
        while True:
            time.sleep(30)
            if not len(self.active_players):
                manager.sendall(json.dumps({"close": "closed the server: no active players"}).encode())
                os._exit(1)

    def spawn_powerups(self):
        while True:
            self.broadcast_message(json.dumps({"powerup_spawn": randint(1,10)}).encode())
            time.sleep(5)


if not network_config['server_manager'] and network_config['local']:
    server = Server([5, 15, 10, 25, 40, 35, 100, 50, 25, False, False, False])