import socket
import threading
import json
from multiprocessing import Process
import string
import random
from Scripts.Network.server import Server

with open("network_config.json") as file:
    network_config = json.load(file)


class Manager:
    def __init__(self):
        self.capacity = 3
        self.threads = []

        self.ip = network_config['manager_ip']
        self.port = 9998

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(5)
        print("[i] Manager started")

        self.database = {
            'server_infos': {},
            'dns': {}
        }

        self.requester = []

        self.hosting_clients = {}

        self.listener()

    def handle_client(self, client):
        ip_port = ""
        dns = ""
        while True:
            # listen for packets
            try:
                request = client.recv(10024)
            except ConnectionResetError:
                break
            if request == b'':
                break
            try:
                decoded_packet = json.loads(request.decode())
                if "host_server" in decoded_packet.keys():
                    if client not in self.hosting_clients:
                        if len(self.database['server_infos']) < self.capacity:
                            self.hosting_clients[client] = ""
                            self.new_server(decoded_packet['host_server'],
                                            decoded_packet['host_server']['matches'])
                            self.requester.append(client)
                            break
                        else:
                            client.sendall(
                                json.dumps({"server_full": "the servers are full please try again later."}).encode()
                            )
                    else:
                        client.sendall(json.dumps({"allready_hosting": self.hosting_clients[client]}).encode())
                if "new_server" in decoded_packet.keys():
                    self.database["server_infos"][decoded_packet['new_server']['ip_port']] = {
                        "ip": decoded_packet['new_server']['ip'],
                        "port": decoded_packet['new_server']['port']
                    }
                    dns = self.generate_dns()
                    self.database['dns'][dns] = {
                        'ip_port': decoded_packet['new_server']['ip_port'],
                        'ip': decoded_packet['new_server']['ip'],
                        'port': decoded_packet['new_server']['port'],
                    }
                    packet = {
                        'dns': dns,
                        'ip_port': decoded_packet['new_server']['ip_port'],
                        "ip": decoded_packet['new_server']['ip'],
                        "port": decoded_packet['new_server']['port']
                    }
                    ip_port = decoded_packet['new_server']['ip_port']
                    self.requester[0].sendall(json.dumps(packet).encode())
                    self.requester.pop(0)
                    self.hosting_clients[client] = dns
                if "close" in decoded_packet.keys():
                    self.database["server_infos"].pop(ip_port)
                    for key, value in self.database["dns"].items():
                        if value == ip_port:
                            self.database['dns'].pop(key)
                            break
                    for key, value in self.hosting_clients.items():
                        if value == dns:
                            self.hosting_clients.pop(key)
                            break
                    print("[-] server {} closed".format(ip_port))
                    break
                if "join" in decoded_packet.keys():
                    try:
                        dns_infos = self.database['dns'][decoded_packet['join']]
                        packet = {
                            'server_info': dns_infos
                        }
                        client.sendall(json.dumps(packet).encode())
                    except KeyError:
                        client.sendall(json.dumps({'no_record': 'please try again'}).encode())

            except json.JSONDecodeError:
                pass

    def listener(self):
        while True:
            client, addr = self.server.accept()
            ip = "{}:{}".format(addr[0], addr[1])
            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            client_handler.start()

    def new_server(self, config, matches):
        server = Process(target=Server, args=(config, matches))
        server.daemon = True
        server.start()
        print("[i] New server started")

    def generate_dns(self, size=3, chars=string.ascii_uppercase + string.digits):
        while True:
            dns = ''.join(random.choice(chars) for _ in range(size))
            if dns not in self.database['dns'].keys():
                return dns


if __name__ == '__main__':
    manager = Manager()
